import 'dart:async';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:frontend_flutter/features/auth/presentation/forgot_password_page.dart';

void main() {
  testWidgets(
    'reset form rejects invalid email before contacting authentication',
    (tester) async {
      await tester.pumpWidget(const MaterialApp(home: ForgotPasswordPage()));
      expect(find.text('Reset password'), findsOneWidget);
      await tester.enterText(find.byType(TextField), 'invalid');
      await tester.tap(find.text('Send reset link'));
      await tester.pump();
      expect(find.text('Enter a valid email address.'), findsOneWidget);
      expect(find.text('Send reset link'), findsOneWidget);
    },
  );
  testWidgets(
    'trims email, prevents duplicate requests, and confirms success',
    (tester) async {
      final pending = Completer<void>();
      final sent = <String>[];
      await tester.pumpWidget(
        MaterialApp(
          home: ForgotPasswordPage(
            sendResetEmail: (email) {
              sent.add(email);
              return pending.future;
            },
          ),
        ),
      );
      await tester.enterText(find.byType(TextField), '  test@example.com  ');
      await tester.tap(find.text('Send reset link'));
      await tester.pump();
      expect(find.text('Sending…'), findsOneWidget);
      expect(
        tester.widget<FilledButton>(find.byType(FilledButton)).onPressed,
        isNull,
      );
      expect(sent, ['test@example.com']);
      pending.complete();
      await tester.pump();
      expect(
        find.textContaining('Check your inbox and spam folder.'),
        findsOneWidget,
      );
    },
  );

  testWidgets('rate limits show an actionable error and allow retry', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        home: ForgotPasswordPage(
          sendResetEmail: (_) async {
            throw FirebaseAuthException(code: 'too-many-requests');
          },
        ),
      ),
    );
    await tester.enterText(find.byType(TextField), 'test@example.com');
    await tester.tap(find.text('Send reset link'));
    await tester.pump();
    expect(
      find.text('Too many reset requests. Please wait before trying again.'),
      findsOneWidget,
    );
    expect(
      tester.widget<FilledButton>(find.byType(FilledButton)).onPressed,
      isNotNull,
    );
  });

  testWidgets('completion after leaving the page is safe', (tester) async {
    final pending = Completer<void>();
    await tester.pumpWidget(
      MaterialApp(
        home: ForgotPasswordPage(sendResetEmail: (_) => pending.future),
      ),
    );
    await tester.enterText(find.byType(TextField), 'test@example.com');
    await tester.tap(find.text('Send reset link'));
    await tester.pumpWidget(const MaterialApp(home: SizedBox()));
    pending.complete();
    await tester.pump();
    expect(tester.takeException(), isNull);
  });
}
