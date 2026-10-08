import 'package:flutter/material.dart';

import '../responsive/responsive_layout.dart';

class LegalLensShell extends StatelessWidget {
  const LegalLensShell({
    super.key,
    required this.desktop,
    required this.mobile,
  });

  final Widget desktop;
  final Widget mobile;

  @override
  Widget build(BuildContext context) {
    return ResponsiveLayout(desktop: desktop, mobile: mobile);
  }
}
