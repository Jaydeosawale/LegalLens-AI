import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../chat/providers/chat_providers.dart';
import '../data/services/platform_api_service.dart';

// ============================================================
// PLATFORM API SERVICE PROVIDER
// ============================================================

final platformApiServiceProvider = Provider<PlatformApiService>((ref) {
  final dio = ref.watch(dioProvider);

  return PlatformApiService(dio);
});
