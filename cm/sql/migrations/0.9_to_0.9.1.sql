INSERT INTO cm_state (id, name) VALUES (10,'amendment');

INSERT INTO cm_workflow_states (id, workflow_id, state_id) VALUES (23, 3, 10);

INSERT INTO cm_workflow_states (id, workflow_id, state_id) VALUES (24, 4, 10);

INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (46, 10, 1);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (47, 10, 2);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (48, 10, 3);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (49, 10, 4);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (50, 10, 5);

INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (42, 46,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (43, 47,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (44, 48,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (45, 49,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (46, 50,107);

