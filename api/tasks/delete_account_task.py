# 修改日期2025-11-04
# 刪除帳號的背景任務，大改善不使用內建功能
import logging

from celery import shared_task

from extensions.ext_database import db
from models import (
    Account,
    AccountIntegrate,
    AppAnnotationHitHistory,
    Conversation,
    DatasetPermission,
    InvitationCode,
    Message,
    MessageAnnotation,
    OperationLog,
    ProviderOrder,
    TenantAccountJoin,
)

logger = logging.getLogger(__name__)


@shared_task(queue="dataset")
def delete_account_task(account_id):
    try:
        account_email = _delete_account_records(account_id)
        db.session.commit()
    except Exception:
        logger.exception("Failed to delete account %s from database.", account_id)
        db.session.rollback()
        raise

    if not account_email:
        logger.error("Account %s not found.", account_id)
        return

    # send success email
    # send_deletion_success_task.delay(account_email)


def _delete_account_records(account_id: str) -> str | None:
    session = db.session
    account = session.query(Account).where(Account.id == account_id).first()
    if not account:
        return None

    account_email = account.email

    # Remove related records in tables referencing the console account.
    session.query(MessageAnnotation).where(MessageAnnotation.account_id == account_id).delete(synchronize_session=False)
    session.query(AppAnnotationHitHistory).where(AppAnnotationHitHistory.account_id == account_id).delete(
        synchronize_session=False
    )
    session.query(OperationLog).where(OperationLog.account_id == account_id).delete(synchronize_session=False)
    session.query(ProviderOrder).where(ProviderOrder.account_id == account_id).delete(synchronize_session=False)
    session.query(DatasetPermission).where(DatasetPermission.account_id == account_id).delete(synchronize_session=False)
    session.query(TenantAccountJoin).where(TenantAccountJoin.account_id == account_id).delete(
        synchronize_session=False
    )
    session.query(AccountIntegrate).where(AccountIntegrate.account_id == account_id).delete(
        synchronize_session=False
    )

    # Invitation codes keep history but clear the deleted account reference.
    session.query(InvitationCode).where(InvitationCode.used_by_account_id == account_id).update(
        {InvitationCode.used_by_account_id: None}, synchronize_session=False
    )

    # Remove message authorship information for the deleted account.
    session.query(Message).where(Message.from_account_id == account_id).update(
        {Message.from_account_id: None}, synchronize_session=False
    )
    session.query(Conversation).where(Conversation.from_account_id == account_id).update(
        {Conversation.from_account_id: None}, synchronize_session=False
    )
    session.query(Conversation).where(Conversation.read_account_id == account_id).update(
        {Conversation.read_account_id: None}, synchronize_session=False
    )

    session.delete(account)

    return account_email
