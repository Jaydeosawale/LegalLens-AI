import 'package:firebase_auth/firebase_auth.dart';

class FirebaseAuthService {
  FirebaseAuthService({FirebaseAuth? firebaseAuth})
    : _firebaseAuth = firebaseAuth ?? FirebaseAuth.instance;

  final FirebaseAuth _firebaseAuth;

  // =========================================================
  // CURRENT USER
  // =========================================================

  User? get currentUser {
    return _firebaseAuth.currentUser;
  }

  // =========================================================
  // AUTH STATE STREAM
  // =========================================================

  Stream<User?> get authStateChanges {
    return _firebaseAuth.authStateChanges();
  }

  // =========================================================
  // LOGIN
  // =========================================================

  Future<UserCredential> signIn({
    required String email,
    required String password,
  }) async {
    return _firebaseAuth.signInWithEmailAndPassword(
      email: email.trim(),
      password: password,
    );
  }

  // =========================================================
  // REGISTER
  // =========================================================

  Future<UserCredential> register({
    required String email,
    required String password,
    String? fullName,
  }) async {
    final credential = await _firebaseAuth.createUserWithEmailAndPassword(
      email: email.trim(),
      password: password,
    );

    if (fullName != null && fullName.trim().isNotEmpty) {
      await credential.user?.updateDisplayName(fullName.trim());
    }

    return credential;
  }

  // =========================================================
  // LOGOUT
  // =========================================================

  Future<void> signOut() async {
    await _firebaseAuth.signOut();
  }

  // =========================================================
  // RESET PASSWORD
  // =========================================================

  Future<void> sendPasswordResetEmail(String email) async {
    await _firebaseAuth.sendPasswordResetEmail(email: email.trim());
  }
}
