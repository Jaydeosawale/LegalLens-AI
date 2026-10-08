import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../chat/providers/chat_providers.dart';
import '../data/services/auth_api_service.dart';

final authApiServiceProvider = Provider<AuthApiService>((ref) {
  final dio = ref.watch(dioProvider);

  return AuthApiService(dio);
});
