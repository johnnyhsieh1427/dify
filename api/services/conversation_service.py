# 修改日期2025-01-13
# 取消自動生成名稱功能
# 在function rename()中，將switch = False永遠不自動生成名稱
# 修改日期2025-01-23
# pagination_by_last_id()中，修改db的get成where
# 修改日期2025-02-28
# rename()中的auto_generate，修改成取前10個字元
from collections.abc import Callable, Sequence
from typing import Optional, Union

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session

from core.app.entities.app_invoke_entities import InvokeFrom
from core.llm_generator.llm_generator import LLMGenerator
from extensions.ext_database import db
from libs.datetime_utils import naive_utc_now
from libs.infinite_scroll_pagination import InfiniteScrollPagination
from models import ConversationVariable
from models.account import Account
from models.model import App, Conversation, EndUser, Message
from services.errors.conversation import (
    ConversationNotExistsError,
    ConversationVariableNotExistsError,
    LastConversationNotExistsError,
)
from services.errors.message import MessageNotExistsError


class ConversationService:
    @classmethod
    def pagination_by_last_id(
        cls,
        *,
        session: Session,
        app_model: App,
        user: Optional[Union[Account, EndUser]],
        last_id: Optional[str],
        limit: int,
        invoke_from: InvokeFrom,
        include_ids: Optional[Sequence[str]] = None,
        exclude_ids: Optional[Sequence[str]] = None,
        sort_by: str = "-updated_at",
    ) -> InfiniteScrollPagination:
        if not user:
            return InfiniteScrollPagination(data=[], limit=limit, has_more=False)
        account_id = (
            user.session_id if isinstance(user, EndUser)
            and db.session.query(Account).where(Account.id == user.session_id)
            else user.id
        )
        stmt = select(Conversation).where(
            Conversation.is_deleted == False,
            Conversation.app_id == app_model.id,
            Conversation.from_source == ("api" if isinstance(user, EndUser) else "console"),
            or_(
                Conversation.from_end_user_id == user.id if isinstance(user, EndUser) else None,
                Conversation.from_account_id == account_id
            ),
            or_(
                Conversation.invoke_from.is_(None),
                Conversation.invoke_from == invoke_from.value
            ),
        )
        if include_ids is not None:
            stmt = stmt.where(Conversation.id.in_(include_ids))
        if exclude_ids is not None:
            stmt = stmt.where(~Conversation.id.in_(exclude_ids))

        # define sort fields and directions
        sort_field, sort_direction = cls._get_sort_params(sort_by)

        if last_id:
            last_conversation = session.scalar(stmt.where(Conversation.id == last_id))
            if not last_conversation:
                raise LastConversationNotExistsError()

            # build filters based on sorting
            filter_condition = cls._build_filter_condition(
                sort_field=sort_field,
                sort_direction=sort_direction,
                reference_conversation=last_conversation,
            )
            stmt = stmt.where(filter_condition)
        query_stmt = stmt.order_by(sort_direction(getattr(Conversation, sort_field))).limit(limit)
        conversations = session.scalars(query_stmt).all()

        has_more = False
        if len(conversations) == limit:
            current_page_last_conversation = conversations[-1]
            rest_filter_condition = cls._build_filter_condition(
                sort_field=sort_field,
                sort_direction=sort_direction,
                reference_conversation=current_page_last_conversation,
            )
            count_stmt = select(func.count()).select_from(stmt.where(rest_filter_condition).subquery())
            rest_count = session.scalar(count_stmt) or 0
            if rest_count > 0:
                has_more = True

        return InfiniteScrollPagination(data=conversations, limit=limit, has_more=has_more)

    @classmethod
    def _get_sort_params(cls, sort_by: str):
        if sort_by.startswith("-"):
            return sort_by[1:], desc
        return sort_by, asc

    @classmethod
    def _build_filter_condition(cls, sort_field: str, sort_direction: Callable, reference_conversation: Conversation):
        field_value = getattr(reference_conversation, sort_field)
        if sort_direction == desc:
            return getattr(Conversation, sort_field) < field_value
        else:
            return getattr(Conversation, sort_field) > field_value

    @classmethod
    def rename(
        cls,
        app_model: App,
        conversation_id: str,
        user: Optional[Union[Account, EndUser]],
        name: str,
        auto_generate: bool,
    ):
        conversation = cls.get_conversation(app_model, conversation_id, user)

        if auto_generate:
            return cls.auto_name_conversation(app_model, conversation)
        else:
            if name in {None, ""}:
                conversation.name = "New conversation"
            else:
                conversation.name = name
            conversation.updated_at = naive_utc_now()
            db.session.commit()

        return conversation
    
    @classmethod
    def auto_name_conversation(cls, app_model: App, conversation: Conversation):
        message = (
            db.session.query(Message)
            .filter(Message.app_id == app_model.id, Message.conversation_id == conversation.id)
            .order_by(Message.created_at.asc())
            .first()
        )

        if not message:
            raise MessageNotExistsError()

        try:
            if len(message.answer) >= 10:
                conversation.name = message.answer[:10] + "..."
            else:
                message_count = (
                    db.session.query(Message)
                    .filter(Message.app_id == app_model.id, Message.conversation_id == conversation.id)
                    .count()
                )
                conversation.name = f"New conversation {message_count}"
        except:
            pass

        db.session.commit()

        return conversation
    
    @classmethod
    def auto_generate_name(cls, app_model: App, conversation: Conversation):
        # get conversation first message
        message = (
            db.session.query(Message)
            .where(Message.app_id == app_model.id, Message.conversation_id == conversation.id)
            .order_by(Message.created_at.asc())
            .first()
        )

        if not message:
            raise MessageNotExistsError()

        # generate conversation name
        try:
            name = LLMGenerator.generate_conversation_name(
                app_model.tenant_id, message.query, conversation.id, app_model.id
            )
            conversation.name = name
        except:
            pass

        db.session.commit()

        return conversation

    @classmethod
    def get_conversation(cls, app_model: App, conversation_id: str, user: Optional[Union[Account, EndUser]]):
        source = "api" if isinstance(user, EndUser) else "console"
        user_id = user.id if user else None
        account_id = (
            user.session_id 
            if isinstance(user, EndUser) and 
            db.session.query(Account).where(Account.id == user.session_id).first()
            else user_id
        )

        conversation_filters = [
            Conversation.id == conversation_id,
            Conversation.app_id == app_model.id,
            Conversation.from_source == source,
            or_(
                Conversation.from_end_user_id == (user_id if isinstance(user, EndUser) else None),
                Conversation.from_account_id == account_id,
            ),
            Conversation.is_deleted == False,
        ]

        conversation = db.session.query(Conversation).where(*conversation_filters).first()

        if not conversation:
            raise ConversationNotExistsError()

        return conversation

    @classmethod
    def delete(cls, app_model: App, conversation_id: str, user: Optional[Union[Account, EndUser]]):
        conversation = cls.get_conversation(app_model, conversation_id, user)

        conversation.is_deleted = True
        conversation.updated_at = naive_utc_now()
        db.session.commit()

    @classmethod
    def get_conversational_variable(
        cls,
        app_model: App,
        conversation_id: str,
        user: Optional[Union[Account, EndUser]],
        limit: int,
        last_id: Optional[str],
    ) -> InfiniteScrollPagination:
        conversation = cls.get_conversation(app_model, conversation_id, user)

        stmt = (
            select(ConversationVariable)
            .where(ConversationVariable.app_id == app_model.id)
            .where(ConversationVariable.conversation_id == conversation.id)
            .order_by(ConversationVariable.created_at)
        )

        with Session(db.engine) as session:
            if last_id:
                last_variable = session.scalar(stmt.where(ConversationVariable.id == last_id))
                if not last_variable:
                    raise ConversationVariableNotExistsError()

                # Filter for variables created after the last_id
                stmt = stmt.where(ConversationVariable.created_at > last_variable.created_at)

            # Apply limit to query
            query_stmt = stmt.limit(limit)  # Get one extra to check if there are more
            rows = session.scalars(query_stmt).all()

        has_more = False
        if len(rows) > limit:
            has_more = True
            rows = rows[:limit]  # Remove the extra item

        variables = [
            {
                "created_at": row.created_at,
                "updated_at": row.updated_at,
                **row.to_variable().model_dump(),
            }
            for row in rows
        ]

        return InfiniteScrollPagination(variables, limit, has_more)
