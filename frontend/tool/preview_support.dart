import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend_flutter/core/auth/user_role.dart';
import 'package:frontend_flutter/features/auth/models/app_user.dart';
import 'package:frontend_flutter/features/auth/providers/auth_provider.dart';
import 'package:frontend_flutter/features/auth/data/services/firebase_auth_service.dart';

class PreviewRole extends Notifier<UserRole> {
  @override
  UserRole build() => UserRole.user;
  void select(UserRole value) => state = value;
}

final previewRoleProvider = NotifierProvider<PreviewRole, UserRole>(
  PreviewRole.new,
);

class PreviewAuth extends AuthNotifier {
  @override
  AuthState build() {
    final role = ref.watch(previewRoleProvider);
    return AuthState(
      isLoading: false,
      user: AppUser(
        id: 'preview-${role.apiValue}',
        email: switch (role) {
          UserRole.user => 'jaydeo@gmail.com',
          UserRole.admin => 'admin@legallens.com',
          UserRole.superAdmin => 'jaydeep.sawale97@gmail.com',
          UserRole.legalProfessional => 'lawyer@example.com',
        },
        fullName: role == UserRole.admin
            ? 'Administrator'
            : role == UserRole.legalProfessional
            ? 'Legal Professional'
            : 'Jaydeo Sawale',
        role: role,
      ),
    );
  }

  @override
  Future<void> refreshProfile() async {}
  @override
  Future<void> logout() async {
    state = const AuthState(isLoading: false);
  }
}

class PreviewFirebaseService implements FirebaseAuthService {
  @override
  Future<void> sendPasswordResetEmail(String email) async {}
  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class PreviewApi {
  final documents = <Map<String, dynamic>>[
    {
      'id': '11111111-1111-4111-8111-111111111111',
      'filename': 'Rental Agreement.pdf',
      'status': 'completed',
      'file_size': 248000,
      'created_at': '2026-10-07T10:00:00',
    },
    {
      'id': '22222222-2222-4222-8222-222222222222',
      'filename': 'Rental Agreement - Revised.pdf',
      'status': 'completed',
      'file_size': 251000,
      'created_at': '2026-10-07T11:00:00',
    },
  ];
  final users = <Map<String, dynamic>>[
    {
      'id': 'u1',
      'full_name': 'Jaydeo Sawale',
      'email': 'jaydeo@gmail.com',
      'role': 'user',
      'is_active': true,
    },
    {
      'id': 'u2',
      'full_name': 'Administrator',
      'email': 'admin@legallens.com',
      'role': 'admin',
      'is_active': true,
    },
    {
      'id': 'u3',
      'full_name': 'Jaydeo Sawale',
      'email': 'jaydeep.sawale97@gmail.com',
      'role': 'super_admin',
      'is_active': true,
    },
  ];
  final permissions = <Map<String, dynamic>>[
    for (final module in [
      'dashboard',
      'documents',
      'research_history',
      'advanced_research',
      'knowledge_base',
      'analytics',
      'users',
    ])
      {
        'module_name': module,
        'enabled_for_admin': true,
        'updated_at': '2026-10-07T10:00:00',
      },
  ];
  final conversations = <Map<String, dynamic>>[
    {
      'id': 'c1',
      'title': 'Rental agreement termination',
      'created_at': '2026-10-07T10:00:00',
      'updated_at': '2026-10-07T10:00:00',
    },
  ];
  final messages = <Map<String, dynamic>>[
    {
      'id': 'm1',
      'role': 'user',
      'content': 'What does the termination clause say?',
      'created_at': '2026-10-07T10:00:00',
    },
    {
      'id': 'm2',
      'role': 'assistant',
      'content':
          '**Sample preview answer:** The agreement provides for written notice before early termination. Check the cited clause for the exact terms.',
      'citations': [
        {'filename': 'Rental Agreement.pdf', 'page': 3},
      ],
      'created_at': '2026-10-07T10:00:01',
    },
  ];
  final settings = <String, dynamic>{
    'model_name': 'openai/gpt-oss-120b',
    'temperature': 0.0,
    'top_k': 8,
  };
  final events = <Map<String, dynamic>>[];
  Dio create() {
    final dio = Dio(BaseOptions(baseUrl: 'https://preview.invalid'));
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (o, h) {
          dynamic data;
          final path = o.path;
          if (path == '/auth/preferences') {
            data =
                o.data ?? {'language': 'English', 'response_style': 'Concise'};
          } else if (path == '/documents/list') {
            data = {
              'documents': documents,
              'total_documents': documents.length,
            };
          } else if (path == '/documents/upload') {
            data = {'success': true, 'duplicates': 0};
          } else if (path.startsWith('/documents/') && o.method == 'DELETE') {
            documents.removeWhere((d) => path.endsWith(d['id']));
            data = {'success': true};
          } else if (path == '/admin/users') {
            data = users;
          } else if (path.startsWith('/admin/users/')) {
            final parts = path.split('/');
            final user = users.firstWhere((u) => u['id'] == parts[3]);
            user.addAll(Map<String, dynamic>.from(o.data));
            data = user;
          } else if (path == '/auth/permissions' ||
              path == '/admin/platform-permissions') {
            data = permissions;
          } else if (path.startsWith('/admin/platform-permissions/')) {
            final item = permissions.firstWhere(
              (p) => path.endsWith(p['module_name'].toString()),
            );
            item.addAll(Map<String, dynamic>.from(o.data));
            data = item;
          } else if (path == '/admin/dashboard' || path == '/admin/analytics') {
            data = {
              'total_users': users.length,
              'total_chats': conversations.length,
              'total_documents': documents.length,
              'total_feedback': 8,
              'positive_feedback': 7,
              'negative_feedback': 1,
            };
          } else if (path == '/admin/chats') {
            data = [
              {
                'id': 'h1',
                'user_email': 'jaydeo@gmail.com',
                'question': 'What does the termination clause say?',
                'answer': messages.last['content'],
                'created_at': '2026-10-07T10:00:00',
              },
            ];
          } else if (path == '/admin/system') {
            data = {
              'settings': settings,
              'health': {
                'database': 'Preview',
                'ai_credentials': 'Preview',
                'documents': documents.length,
                'chunks': 84,
                'vectors': 84,
              },
              'events': events,
            };
          } else if (path == '/admin/system/settings') {
            settings.addAll(Map<String, dynamic>.from(o.data));
            events.insert(0, {
              'action': 'Updated AI and retrieval configuration',
              'actor': 'Preview administrator',
              'created_at': DateTime.now().toIso8601String(),
            });
            data = settings;
          } else if (path == '/conversations/') {
            data = conversations;
          } else if (path.startsWith('/conversations/')) {
            if (o.method == 'DELETE') {
              conversations.removeWhere((c) => path.endsWith(c['id']));
              data = null;
            } else if (o.method == 'PATCH') {
              conversations.first.addAll(Map<String, dynamic>.from(o.data));
              data = conversations.first;
            } else {
              data = {...conversations.first, 'messages': messages};
            }
          } else if (path == '/chat/') {
            final form = o.data as FormData;
            final question = form.fields
                .firstWhere((f) => f.key == 'question')
                .value;
            final isCompare = question.startsWith('Compare');
            data = {
              'chat_id': 'preview-answer',
              'conversation_id': 'c1',
              'answer': isCompare
                  ? '**Sample preview comparison**\n\n| Clause | Original | Revised |\n|---|---|---|\n| Notice | 30 days | 60 days |\n\nThe revised agreement changes the notice period. Verify the source clauses before acting.'
                  : '**Sample preview summary**\n\nThis rental agreement records the parties, monthly rent, deposit, and termination conditions.\n\n- Check payment dates and deposit deductions.\n- Review notice requirements before terminating.',
              'citations': [
                {'filename': 'Rental Agreement.pdf', 'page': 3},
              ],
            };
          } else if (path == '/auth/me') {
            data = {
              'id': 'preview',
              'full_name': (o.data as Map?)?['full_name'] ?? 'Jaydeo Sawale',
              'email': 'jaydeo@gmail.com',
              'role': 'user',
            };
          } else {
            h.reject(
              DioException(
                requestOptions: o,
                error: 'Unsupported preview request: $path',
              ),
            );
            return;
          }
          h.resolve(
            Response(
              requestOptions: o,
              statusCode: o.method == 'DELETE' ? 204 : 200,
              data: data == null ? null : jsonDecode(jsonEncode(data)),
            ),
          );
        },
      ),
    );
    return dio;
  }
}
