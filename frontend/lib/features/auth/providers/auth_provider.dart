import 'dart:async';

import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/auth/user_role.dart';

import '../data/services/auth_api_service.dart';
import '../data/services/firebase_auth_service.dart';
import '../models/app_user.dart';
import 'auth_api_provider.dart';

// =========================================================
// FIREBASE AUTH SERVICE PROVIDER
// =========================================================

final firebaseAuthServiceProvider = Provider<FirebaseAuthService>((ref) {
  return FirebaseAuthService();
});

// =========================================================
// AUTH STATE
// =========================================================

class AuthState {
  const AuthState({this.user, this.isLoading = true, this.errorMessage});

  final AppUser? user;
  final bool isLoading;
  final String? errorMessage;

  bool get isAuthenticated => user != null;

  UserRole? get role => user?.role;

  AuthState copyWith({
    AppUser? user,
    bool? isLoading,
    String? errorMessage,
    bool clearUser = false,
    bool clearError = false,
  }) {
    return AuthState(
      user: clearUser ? null : user ?? this.user,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }
}

// =========================================================
// AUTH NOTIFIER
// =========================================================

class AuthNotifier extends Notifier<AuthState> {
  StreamSubscription<User?>? _authSubscription;

  late FirebaseAuthService _authService;
  late AuthApiService _authApiService;

  @override
  AuthState build() {
    _authService = ref.read(firebaseAuthServiceProvider);
    _authApiService = ref.read(authApiServiceProvider);

    _listenToAuthChanges();

    ref.onDispose(() {
      _authSubscription?.cancel();
    });

    return const AuthState(isLoading: true);
  }

  // =========================================================
  // FIREBASE AUTH STATE LISTENER
  // =========================================================

  void _listenToAuthChanges() {
    _authSubscription = _authService.authStateChanges.listen(
      (firebaseUser) async {
        if (firebaseUser == null) {
          state = const AuthState(isLoading: false);
          return;
        }

        await _loadCurrentUser(firebaseUser);
      },
      onError: (Object error) {
        state = AuthState(isLoading: false, errorMessage: error.toString());
      },
    );
  }

  // =========================================================
  // LOAD CURRENT LEGALLENS USER
  // =========================================================

  Future<void> _loadCurrentUser(User firebaseUser) async {
    try {
      // Force-refresh token before calling backend.
      await firebaseUser.getIdToken(true);

      // Load real LegalLens user + role from PostgreSQL.
      final appUser = await _authApiService.getCurrentUser();

      state = AuthState(user: appUser, isLoading: false);
    } catch (error) {
      state = AuthState(isLoading: false, errorMessage: error.toString());
    }
  }

  // =========================================================
  // LOGIN
  // =========================================================

  Future<void> signIn({required String email, required String password}) async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      // Firebase authentication only.
      //
      // The Firebase auth listener is the single source of truth
      // and will automatically call:
      //
      // GET /auth/me
      //
      // to load the real LegalLens user and role.
      await _authService.signIn(email: email.trim(), password: password);
    } on FirebaseAuthException catch (error) {
      state = AuthState(
        isLoading: false,
        errorMessage: _firebaseErrorMessage(error),
      );

      rethrow;
    } catch (error) {
      state = AuthState(
        isLoading: false,
        errorMessage: 'Unable to sign in. Please try again.',
      );

      rethrow;
    }
  }

  // =========================================================
  // REGISTER
  // =========================================================

  Future<void> register({
    required String fullName,
    required String email,
    required String password,
  }) async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      await _authService.register(
        email: email.trim(),
        password: password,
        fullName: fullName.trim(),
      );

      // Firebase automatically signs in a newly created user.
      // LegalLens UX requires manual sign-in after registration.
      await _authService.signOut();

      state = const AuthState(isLoading: false);
    } on FirebaseAuthException catch (error) {
      state = AuthState(
        isLoading: false,
        errorMessage: _firebaseErrorMessage(error),
      );

      rethrow;
    } catch (_) {
      state = const AuthState(
        isLoading: false,
        errorMessage: 'Unable to create your account. Please try again.',
      );

      rethrow;
    }
  }

  // =========================================================
  // LOGOUT
  // =========================================================

  Future<void> logout() async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      await _authService.signOut();

      state = const AuthState(isLoading: false);
    } on FirebaseAuthException catch (error) {
      state = AuthState(
        isLoading: false,
        errorMessage: _firebaseErrorMessage(error),
      );

      rethrow;
    }
  }

  Future<void> refreshProfile() async {
    final appUser = await _authApiService.getCurrentUser();
    state = AuthState(user: appUser, isLoading: false);
  }

  // =========================================================
  // PASSWORD RESET
  // =========================================================

  Future<void> sendPasswordResetEmail(String email) async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      await _authService.sendPasswordResetEmail(email);

      state = state.copyWith(isLoading: false);
    } on FirebaseAuthException catch (error) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: _firebaseErrorMessage(error),
      );

      rethrow;
    }
  }

  // =========================================================
  // CLEAR ERROR
  // =========================================================

  void clearError() {
    state = state.copyWith(clearError: true);
  }

  // =========================================================
  // FIREBASE ERROR MESSAGES
  // =========================================================

  String _firebaseErrorMessage(FirebaseAuthException error) {
    switch (error.code) {
      case 'invalid-email':
        return 'Please enter a valid email address.';

      case 'user-not-found':
      case 'wrong-password':
      case 'invalid-credential':
      case 'invalid-login-credentials':
        return 'Incorrect email or password.';

      case 'email-already-in-use':
        return 'An account already exists with this email.';

      case 'weak-password':
        return 'Please choose a stronger password.';

      case 'too-many-requests':
        return 'Too many attempts. Please try again later.';

      case 'network-request-failed':
        return 'Network error. Please check your connection.';

      default:
        return error.message ?? 'Authentication failed. Please try again.';
    }
  }
}

// =========================================================
// AUTH PROVIDER
// =========================================================

final authProvider = NotifierProvider<AuthNotifier, AuthState>(
  AuthNotifier.new,
);
