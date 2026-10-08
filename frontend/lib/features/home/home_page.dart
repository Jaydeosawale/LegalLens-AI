import 'package:flutter/material.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return const _DashboardContent();
  }
}

class _DashboardContent extends StatelessWidget {
  const _DashboardContent();

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isMobile = constraints.maxWidth < 600;

        return SingleChildScrollView(
          padding: EdgeInsets.all(isMobile ? 20 : 32),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 1400),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // =====================================================
                // HEADER
                // =====================================================
                const Text(
                  'Welcome to Legal Lens',
                  style: TextStyle(fontSize: 32, fontWeight: FontWeight.w700),
                ),

                const SizedBox(height: 8),

                Text(
                  'Your intelligent legal research and document assistant.',
                  style: TextStyle(fontSize: 16, color: Colors.grey.shade600),
                ),

                const SizedBox(height: 32),

                // =====================================================
                // STATISTICS
                // =====================================================
                Wrap(
                  spacing: 16,
                  runSpacing: 16,
                  children: [
                    const _StatCard(
                      icon: Icons.chat_bubble_outline_rounded,
                      value: '0',
                      label: 'Conversations',
                    ),
                    const _StatCard(
                      icon: Icons.description_outlined,
                      value: '0',
                      label: 'Documents',
                    ),
                    const _StatCard(
                      icon: Icons.auto_awesome_rounded,
                      value: 'Ready',
                      label: 'AI Assistant',
                    ),
                  ],
                ),

                const SizedBox(height: 40),

                // =====================================================
                // GET STARTED
                // =====================================================
                const Text(
                  'Get Started',
                  style: TextStyle(fontSize: 22, fontWeight: FontWeight.w700),
                ),

                const SizedBox(height: 20),

                Wrap(
                  spacing: 16,
                  runSpacing: 16,
                  children: const [
                    _ActionCard(
                      icon: Icons.auto_awesome_rounded,
                      title: 'Ask Legal Lens',
                      description:
                          'Ask questions and explore legal information with AI.',
                    ),
                    _ActionCard(
                      icon: Icons.upload_file_rounded,
                      title: 'Upload Documents',
                      description:
                          'Upload legal documents for AI-powered analysis.',
                    ),
                    _ActionCard(
                      icon: Icons.history_rounded,
                      title: 'View History',
                      description:
                          'Continue your previous legal research conversations.',
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

// =====================================================
// STAT CARD
// =====================================================

class _StatCard extends StatelessWidget {
  const _StatCard({
    required this.icon,
    required this.value,
    required this.label,
  });

  final IconData icon;
  final String value;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 230,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: Theme.of(context).colorScheme.primary),

          const SizedBox(height: 18),

          Text(
            value,
            style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w700),
          ),

          const SizedBox(height: 4),

          Text(label, style: TextStyle(color: Colors.grey.shade600)),
        ],
      ),
    );
  }
}

// =====================================================
// ACTION CARD
// =====================================================

class _ActionCard extends StatelessWidget {
  const _ActionCard({
    required this.icon,
    required this.title,
    required this.description,
  });

  final IconData icon;
  final String title;
  final String description;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 300,
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 30, color: Theme.of(context).colorScheme.primary),

          const SizedBox(height: 18),

          Text(
            title,
            style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w700),
          ),

          const SizedBox(height: 8),

          Text(
            description,
            style: TextStyle(height: 1.5, color: Colors.grey.shade600),
          ),
        ],
      ),
    );
  }
}
