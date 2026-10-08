import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:frontend_flutter/core/widgets/legal_lens_logo.dart';
import 'package:frontend_flutter/features/chat/domain/models/chat_models.dart';
import 'package:frontend_flutter/features/chat/widgets/chat_messages.dart';

void main() {
  testWidgets('LegalLens logo asset is available', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: Scaffold(body: LegalLensLogo())),
    );
    await tester.pumpAndSettle();

    expect(find.byType(LegalLensLogo), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('Chat answer shows its source document and page', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: ChatMessages(
            isLoading: false,
            messages: [
              ChatMessage(
                id: 'answer-1',
                content: 'Answer from the source.',
                role: MessageRole.assistant,
                createdAt: DateTime(2026, 10, 7),
                citations: const [
                  ChatCitation(filename: 'source.pdf', page: 2),
                ],
              ),
            ],
          ),
        ),
      ),
    );

    expect(find.textContaining('source.pdf'), findsOneWidget);
    expect(find.textContaining('p. 2'), findsOneWidget);
  });
}
