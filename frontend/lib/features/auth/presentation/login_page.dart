import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_colors.dart';
import '../providers/auth_provider.dart';

class LoginPage extends ConsumerStatefulWidget {
  const LoginPage({super.key});

  @override
  ConsumerState<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends ConsumerState<LoginPage> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  final _formKey = GlobalKey<FormState>();

  bool _obscurePassword = true;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    try {
      await ref
          .read(authProvider.notifier)
          .signIn(
            email: _emailController.text,
            password: _passwordController.text,
          );
    } catch (_) {
      // Error is handled through AuthState.
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final authState = ref.watch(authProvider);

    ref.listen<AuthState>(authProvider, (previous, next) {
      if (next.isAuthenticated && previous?.isAuthenticated != true) {
        context.go('/home');
        return;
      }
      if (next.errorMessage != null &&
          next.errorMessage != previous?.errorMessage) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(next.errorMessage!),
            backgroundColor: AppColors.error,
          ),
        );
      }
    });

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 460),
              child: Card(
                child: Padding(
                  padding: const EdgeInsets.all(32),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // =====================================
                        // LEGALLENS BRAND
                        // =====================================

                        Center(
                          child: Container(
                            width: 72,
                            height: 72,
                            decoration: BoxDecoration(
                              color: AppColors.antiqueGoldLight,
                              borderRadius: BorderRadius.circular(14),
                              border: Border.all(
                                color: AppColors.antiqueGold.withValues(
                                  alpha: 0.18,
                                ),
                              ),
                            ),
                            child: Padding(
                              padding: const EdgeInsets.all(10),
                              child: Image.asset(
                                'assets/images/legallens_logo.png',
                                fit: BoxFit.contain,
                              ),
                            ),
                          ),
                        ),

                        const SizedBox(height: 20),

                        Text(
                          'Welcome back',
                          textAlign: TextAlign.center,
                          style: theme.textTheme.headlineMedium,
                        ),

                        const SizedBox(height: 8),

                        Text(
                          'Sign in to Legal Lens.',
                          textAlign: TextAlign.center,
                          style: theme.textTheme.bodyMedium,
                        ),

                        const SizedBox(height: 32),

                        // =====================================
                        // EMAIL
                        // =====================================
                        TextFormField(
                          controller: _emailController,
                          keyboardType: TextInputType.emailAddress,
                          textInputAction: TextInputAction.next,
                          decoration: const InputDecoration(
                            labelText: 'Email address',
                            prefixIcon: Icon(Icons.email_outlined),
                          ),
                          validator: (value) {
                            final email = value?.trim() ?? '';

                            if (email.isEmpty) {
                              return 'Please enter your email address.';
                            }

                            if (!email.contains('@')) {
                              return 'Please enter a valid email address.';
                            }

                            return null;
                          },
                        ),

                        const SizedBox(height: 16),

                        // =====================================
                        // PASSWORD
                        // =====================================
                        TextFormField(
                          controller: _passwordController,
                          obscureText: _obscurePassword,
                          textInputAction: TextInputAction.done,
                          onFieldSubmitted: (_) {
                            if (!authState.isLoading) {
                              _login();
                            }
                          },
                          decoration: InputDecoration(
                            labelText: 'Password',
                            prefixIcon: const Icon(Icons.lock_outline),
                            suffixIcon: IconButton(
                              icon: Icon(
                                _obscurePassword
                                    ? Icons.visibility_outlined
                                    : Icons.visibility_off_outlined,
                              ),
                              onPressed: () {
                                setState(() {
                                  _obscurePassword = !_obscurePassword;
                                });
                              },
                            ),
                          ),
                          validator: (value) {
                            if (value == null || value.isEmpty) {
                              return 'Please enter your password.';
                            }

                            if (value.length < 6) {
                              return 'Password must be at least 6 characters.';
                            }

                            return null;
                          },
                        ),

                        const SizedBox(height: 8),

                        Align(
                          alignment: Alignment.centerRight,
                          child: TextButton(
                            onPressed: authState.isLoading
                                ? null
                                : () {
                                    context.go('/forgot-password');
                                  },
                            child: const Text('Forgot password?'),
                          ),
                        ),

                        const SizedBox(height: 12),

                        // =====================================
                        // SIGN IN
                        // =====================================
                        SizedBox(
                          height: 52,
                          child: FilledButton(
                            onPressed: authState.isLoading ? null : _login,
                            child: authState.isLoading
                                ? const SizedBox(
                                    width: 22,
                                    height: 22,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                      color: AppColors.textOnDark,
                                    ),
                                  )
                                : const Text('Sign In'),
                          ),
                        ),

                        const SizedBox(height: 28),

                        // =====================================
                        // REGISTER
                        // =====================================
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Text('New to Legal Lens?'),
                            TextButton(
                              onPressed: authState.isLoading
                                  ? null
                                  : () {
                                      context.go('/register');
                                    },
                              child: const Text('Create account'),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
