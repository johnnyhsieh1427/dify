# 修改日期2025-02-28
# 新增create_workspace功能
# 修改日期2025-07-23
# 新增create_account功能

from dify_app import DifyApp


def init_app(app: DifyApp):
    from commands import (
        add_qdrant_index,
        clear_free_plan_tenant_expired_logs,
        clear_orphaned_file_records,
        convert_to_agent_apps,
        create_account,
        create_tenant,
        create_workspace,
        delete_account,
        extract_plugins,
        extract_unique_plugins,
        fix_app_site_missing,
        install_plugins,
        migrate_data_for_plugin,
        old_metadata_migration,
        remove_orphaned_files_on_storage,
        reset_email,
        reset_encrypt_key_pair,
        reset_password,
        upgrade_db,
        vdb_migrate,
    )

    cmds_to_register = [
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
        vdb_migrate,
        convert_to_agent_apps,
        add_qdrant_index,
        create_tenant,
        upgrade_db,
        fix_app_site_missing,
        migrate_data_for_plugin,
        extract_plugins,
        extract_unique_plugins,
        install_plugins,
        old_metadata_migration,
        clear_free_plan_tenant_expired_logs,
        clear_orphaned_file_records,
        remove_orphaned_files_on_storage,
        create_account,
    ]
    for cmd in cmds_to_register:
        app.cli.add_command(cmd)
