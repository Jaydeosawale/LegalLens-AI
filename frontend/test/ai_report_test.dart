import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:frontend_flutter/core/widgets/release_safety.dart';
import 'package:frontend_flutter/features/chat/providers/chat_providers.dart';

void main() {
  testWidgets('failed report stays open and retry submits the selected answer', (tester) async {
    final dio = Dio();
    var attempts = 0;
    dio.interceptors.add(InterceptorsWrapper(onRequest: (options, handler) {
      attempts++;
      expect(options.path, '/content-reports');
      expect(options.data['content'], 'Synthetic answer');
      if (attempts == 1) {
        handler.reject(DioException(requestOptions: options));
      } else {
        handler.resolve(Response(requestOptions: options, statusCode: 201, data: {'id': 'report-id', 'status': 'pending'}));
      }
    }));
    await tester.pumpWidget(ProviderScope(overrides: [dioProvider.overrideWithValue(dio)], child: const MaterialApp(home: Scaffold(body: ReportAiAnswer(content: 'Synthetic answer')))));
    await tester.tap(find.text('Report AI answer'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Submit report'));
    await tester.pumpAndSettle();
    expect(find.textContaining('Report could not be sent'), findsOneWidget);
    await tester.tap(find.text('Submit report'));
    await tester.pumpAndSettle();
    expect(attempts, 2);
    expect(find.text('Report submitted for review. Thank you.'), findsOneWidget);
  });
}
