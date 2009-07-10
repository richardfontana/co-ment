-- postgresql specific sequence value setting
-- to avoid conflict with manually inserted values

SELECT setval('auth_permission_id_seq', 1000);

SELECT setval('cm_role_id_seq', 1000);
SELECT setval('cm_role_permissions_id_seq', 1000);

SELECT setval('cm_state_id_seq', 1000);

SELECT setval('cm_workflow_id_seq', 1000);
SELECT setval('cm_workflow_states_id_seq', 1000);

SELECT setval('cm_staterolepermissions_id_seq', 1000);
SELECT setval('cm_staterolepermissions_permissions_id_seq', 1000);

