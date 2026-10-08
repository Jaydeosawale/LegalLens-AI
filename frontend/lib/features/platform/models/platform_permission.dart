class PlatformPermission {
  const PlatformPermission({
    required this.moduleName,
    required this.enabledForAdmin,
    required this.updatedAt,
  });

  final String moduleName;
  final bool enabledForAdmin;
  final DateTime updatedAt;

  factory PlatformPermission.fromJson(Map<String, dynamic> json) {
    return PlatformPermission(
      moduleName: json['module_name'] as String,
      enabledForAdmin: json['enabled_for_admin'] as bool,
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  PlatformPermission copyWith({bool? enabledForAdmin}) {
    return PlatformPermission(
      moduleName: moduleName,
      enabledForAdmin: enabledForAdmin ?? this.enabledForAdmin,
      updatedAt: updatedAt,
    );
  }
}
