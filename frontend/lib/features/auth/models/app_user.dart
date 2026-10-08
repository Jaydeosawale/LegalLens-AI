import '../../../core/auth/user_role.dart';

class AppUser {
  const AppUser({
    required this.id,
    required this.email,
    required this.role,
    this.fullName,
  });

  final String id;
  final String email;
  final String? fullName;
  final UserRole role;

  factory AppUser.fromJson(Map<String, dynamic> json) {
    return AppUser(
      id: json['id'].toString(),
      email: json['email'] as String,
      fullName: json['full_name'] as String?,
      role: UserRoleExtension.fromApi(json['role'] as String?),
    );
  }
}
