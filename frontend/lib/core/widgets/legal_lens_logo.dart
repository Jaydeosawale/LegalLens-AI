import 'package:flutter/material.dart';

class LegalLensLogo extends StatelessWidget {
  const LegalLensLogo({super.key, this.size = 40, this.fit = BoxFit.contain});

  final double size;
  final BoxFit fit;

  @override
  Widget build(BuildContext context) {
    return Image.asset(
      'assets/images/legallens_logo.png',
      width: size,
      height: size,
      fit: fit,
      filterQuality: FilterQuality.high,
    );
  }
}
