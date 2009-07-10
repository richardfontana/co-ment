-- This is the general initialisation for co-ment
-------------------------------------------------
-- this file populate tables:
-- auth_permission
-- cm_role
-- cm_state
-- cm_workflow
-- cm_staterolepermissions

--auth.permission
INSERT INTO auth_permission (id,codename,name,content_type_id) VALUES (100,'can_view_local_text','Can view local text',(select id from django_content_type where name =
'text')); 
INSERT INTO auth_permission (id,codename,name,content_type_id) VALUES (101,'can_add_comment_local_text','Can add comment local text',(select id from django_content_type where name =
'text'));
INSERT INTO auth_permission (id,codename,name,content_type_id) VALUES (102,'can_edit_local_text','Can edit local text',(select id from django_content_type where name =
'text'));
INSERT INTO auth_permission (id,codename,name,content_type_id) VALUES (103,'can_change_settings_local_text','Can change settings local text',(select id from django_content_type where name =
'text'));
INSERT INTO auth_permission (id,codename,name,content_type_id) VALUES (104,'can_delete_local_text','Can delete local text',(select id from django_content_type where name =
'text'));
INSERT INTO auth_permission (id,codename,name,content_type_id) VALUES (105,'can_manage_comment_local_text','Can manage comment local text',(select id from django_content_type where name =
'text'));
INSERT INTO auth_permission (id,codename,name,content_type_id) VALUES (106,'can_delete_local_version','Can delete local version',(select id from django_content_type where name =
'text'));
INSERT INTO auth_permission (id,codename,name,content_type_id) VALUES (107,'can_view_comment_local_text','Can view comment local text',(select id from django_content_type where name =
'text'));

--cm.role
INSERT INTO cm_role (id,name,"order") VALUES (1,'Owner',20);
INSERT INTO cm_role (id,name,"order") VALUES (2,'Observer',10);
INSERT INTO cm_role (id,name,"order") VALUES (3,'Editor',15);
INSERT INTO cm_role (id,name,"order") VALUES (4,'Commenter',12);
INSERT INTO cm_role (id,name,"order") VALUES (5,'Moderator',13);


INSERT INTO cm_role_permissions (id, role_id, permission_id) VALUES (1,1,100);
INSERT INTO cm_role_permissions (id, role_id, permission_id) VALUES (2,1,101);
INSERT INTO cm_role_permissions (id, role_id, permission_id) VALUES (3,1,102);
INSERT INTO cm_role_permissions (id, role_id, permission_id) VALUES (4,1,103);
INSERT INTO cm_role_permissions (id, role_id, permission_id) VALUES (5,1,104);
INSERT INTO cm_role_permissions (id, role_id, permission_id) VALUES (6,1,105);
INSERT INTO cm_role_permissions (id, role_id, permission_id) VALUES (7,1,106);
INSERT INTO cm_role_permissions (id, role_id, permission_id) VALUES (8,1,107);

INSERT INTO cm_role_permissions (id, role_id, permission_id) VALUES (9,2,100);
INSERT INTO cm_role_permissions (id, role_id, permission_id) VALUES (10,2,107);

INSERT INTO cm_role_permissions (id, role_id, permission_id) VALUES (11,3,100);
INSERT INTO cm_role_permissions (id, role_id, permission_id) VALUES (12,3,101);
INSERT INTO cm_role_permissions (id, role_id, permission_id) VALUES (13,3,102);
INSERT INTO cm_role_permissions (id, role_id, permission_id) VALUES (14,3,107);
INSERT INTO cm_role_permissions (id, role_id, permission_id) VALUES (15,3,105);

INSERT INTO cm_role_permissions (id, role_id, permission_id) VALUES (16,4,100);
INSERT INTO cm_role_permissions (id, role_id, permission_id) VALUES (17,4,101);
INSERT INTO cm_role_permissions (id, role_id, permission_id) VALUES (18,4,107);

INSERT INTO cm_role_permissions (id, role_id, permission_id) VALUES (19,5,100);
INSERT INTO cm_role_permissions (id, role_id, permission_id) VALUES (20,5,101);
INSERT INTO cm_role_permissions (id, role_id, permission_id) VALUES (21,5,105);
INSERT INTO cm_role_permissions (id, role_id, permission_id) VALUES (22,5,107);

--cm.state
INSERT INTO cm_state (id, name) VALUES (1,'pending');
INSERT INTO cm_state (id, name) VALUES (2,'visible');
INSERT INTO cm_state (id, name) VALUES (3,'published');
INSERT INTO cm_state (id, name) VALUES (4,'rejected');
INSERT INTO cm_state (id, name) VALUES (5,'ignored');
INSERT INTO cm_state (id, name) VALUES (6,'redundant');
INSERT INTO cm_state (id, name) VALUES (7,'issue');
INSERT INTO cm_state (id, name) VALUES (8,'oked');
INSERT INTO cm_state (id, name) VALUES (9,'done');
INSERT INTO cm_state (id, name) VALUES (10,'amendment');

--cm.workflow
INSERT INTO cm_workflow (id, name, initial_state_id) VALUES (1,'simple a priori moderation workflow',1);
INSERT INTO cm_workflow (id, name, initial_state_id) VALUES (2,'simple a posteriori moderation workflow',2);
INSERT INTO cm_workflow (id, name, initial_state_id) VALUES (3,'rich a priori moderation workflow',1);
INSERT INTO cm_workflow (id, name, initial_state_id) VALUES (4,'rich a posteriori moderation workflow',2);

INSERT INTO cm_workflow_states (id, workflow_id, state_id) VALUES (1, 1, 1);
INSERT INTO cm_workflow_states (id, workflow_id, state_id) VALUES (2, 1, 3);
INSERT INTO cm_workflow_states (id, workflow_id, state_id) VALUES (3, 1, 4);

INSERT INTO cm_workflow_states (id, workflow_id, state_id) VALUES (4, 2, 2);
INSERT INTO cm_workflow_states (id, workflow_id, state_id) VALUES (5, 2, 3);
INSERT INTO cm_workflow_states (id, workflow_id, state_id) VALUES (6, 2, 4);

INSERT INTO cm_workflow_states (id, workflow_id, state_id) VALUES (7, 3, 1);
INSERT INTO cm_workflow_states (id, workflow_id, state_id) VALUES (8, 3, 3);
INSERT INTO cm_workflow_states (id, workflow_id, state_id) VALUES (9, 3, 4);
INSERT INTO cm_workflow_states (id, workflow_id, state_id) VALUES (10, 3, 5);
INSERT INTO cm_workflow_states (id, workflow_id, state_id) VALUES (11, 3, 6);
INSERT INTO cm_workflow_states (id, workflow_id, state_id) VALUES (12, 3, 7);
INSERT INTO cm_workflow_states (id, workflow_id, state_id) VALUES (13, 3, 8);
INSERT INTO cm_workflow_states (id, workflow_id, state_id) VALUES (14, 3, 9);
INSERT INTO cm_workflow_states (id, workflow_id, state_id) VALUES (23, 3, 10);

INSERT INTO cm_workflow_states (id, workflow_id, state_id) VALUES (15, 4, 2);
INSERT INTO cm_workflow_states (id, workflow_id, state_id) VALUES (16, 4, 3);
INSERT INTO cm_workflow_states (id, workflow_id, state_id) VALUES (17, 4, 4);
INSERT INTO cm_workflow_states (id, workflow_id, state_id) VALUES (18, 4, 5);
INSERT INTO cm_workflow_states (id, workflow_id, state_id) VALUES (19, 4, 6);
INSERT INTO cm_workflow_states (id, workflow_id, state_id) VALUES (20, 4, 7);
INSERT INTO cm_workflow_states (id, workflow_id, state_id) VALUES (21, 4, 8);
INSERT INTO cm_workflow_states (id, workflow_id, state_id) VALUES (22, 4, 9);
INSERT INTO cm_workflow_states (id, workflow_id, state_id) VALUES (24, 4, 10);

--cm.staterolepermissions
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (1, 1, 1);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (2, 1, 2);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (3, 1, 3);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (4, 1, 4);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (5, 1, 5);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (6, 2, 1);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (7, 2, 2);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (8, 2, 3);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (9, 2, 4);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (10, 2, 5);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (11, 3, 1);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (12, 3, 2);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (13, 3, 3);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (14, 3, 4);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (15, 3, 5);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (16, 4, 1);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (17, 4, 2);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (18, 4, 3);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (19, 4, 4);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (20, 4, 5);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (21, 5, 1);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (22, 5, 2);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (23, 5, 3);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (24, 5, 4);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (25, 5, 5);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (26, 6, 1);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (27, 6, 2);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (28, 6, 3);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (29, 6, 4);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (30, 6, 5);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (31, 7, 1);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (32, 7, 2);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (33, 7, 3);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (34, 7, 4);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (35, 7, 5);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (36, 8, 1);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (37, 8, 2);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (38, 8, 3);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (39, 8, 4);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (40, 8, 5);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (41, 9, 1);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (42, 9, 2);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (43, 9, 3);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (44, 9, 4);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (45, 9, 5);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (46, 10, 1);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (47, 10, 2);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (48, 10, 3);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (49, 10, 4);
INSERT INTO cm_staterolepermissions (id, state_id, role_id) VALUES (50, 10, 5);

INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (1, 1,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (2, 3,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (3, 5,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (4, 6,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (5, 7,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (6, 8,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (7, 9,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (8, 10,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (9, 11,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (10, 12,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (11, 13,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (12, 14,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (13, 15,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (14, 16,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (15, 18,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (16, 20,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (17, 21,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (18, 22,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (19, 23,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (20, 24,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (21, 25,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (22, 26,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (23, 27,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (24, 28,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (25, 29,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (26, 30,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (27, 31,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (28, 32,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (29, 33,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (30, 34,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (31, 35,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (32, 36,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (33, 37,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (34, 38,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (35, 39,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (36, 40,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (37, 41,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (38, 42,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (39, 43,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (40, 44,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (41, 45,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (42, 46,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (43, 47,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (44, 48,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (45, 49,107);
INSERT INTO cm_staterolepermissions_permissions (id, staterolepermissions_id, permission_id) VALUES (46, 50,107);

