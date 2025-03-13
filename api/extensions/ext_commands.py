# 修改日期2025-02-28
# 新增create_workspace功能

from dify_app import DifyApp


def init_app(app: DifyApp):
    from commands import (
        add_qdrant_doc_id_index,
        convert_to_agent_apps,
        create_tenant,
        create_workspace,
        delete_account,
        extract_plugins,
        extract_unique_plugins,
        fix_app_site_missing,
        install_plugins,
        migrate_data_for_plugin,
        reset_email,
        reset_encrypt_key_pair,
        reset_password,
        upgrade_db,
        vdb_migrate,
    )

    cmds_to_register = [
        add_qdrant_doc_id_index,
        convert_to_agent_apps,
        create_tenant,
        create_workspace,
        delete_account,
        extract_plugins,
        extract_unique_plugins,
        fix_app_site_missing,
        install_plugins,
        migrate_data_for_plugin,
        reset_password,
        reset_email,
        reset_encrypt_key_pair,
        upgrade_db,
        vdb_migrate,
        convert_to_agent_apps,
        add_qdrant_doc_id_index,
        create_tenant,
        upgrade_db,
        fix_app_site_missing,
    ]
    for cmd in cmds_to_register:
        app.cli.add_command(cmd)
