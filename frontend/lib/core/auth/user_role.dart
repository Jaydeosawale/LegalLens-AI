enum UserRole { user, legalProfessional, admin, superAdmin }

extension UserRoleExtension on UserRole {
  bool get isAdministrator =>
      this == UserRole.admin || this == UserRole.superAdmin;
  String get apiValue {
    switch (this) {
      case UserRole.user:
        return 'user';
      case UserRole.legalProfessional:
        return 'legal_professional';

      case UserRole.admin:
        return 'admin';

      case UserRole.superAdmin:
        return 'super_admin';
    }
  }

  String get displayName {
    switch (this) {
      case UserRole.user:
        return 'User';
      case UserRole.legalProfessional:
        return 'Legal Professional';

      case UserRole.admin:
        return 'Admin';

      case UserRole.superAdmin:
        return 'Super Admin';
    }
  }

  static UserRole fromApi(String? role) {
    switch (role?.toLowerCase()) {
      case 'superadmin':
      case 'super_admin':
        return UserRole.superAdmin;

      case 'admin':
        return UserRole.admin;
      case 'legal_professional':
      case 'lawyer':
        return UserRole.legalProfessional;

      default:
        return UserRole.user;
    }
  }
}
