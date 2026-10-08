import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';

class ChatWelcome extends StatelessWidget {
  const ChatWelcome({super.key, required this.onSuggestionSelected});

  final ValueChanged<String> onSuggestionSelected;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(32),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 850),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 72,
                height: 72,
                decoration: BoxDecoration(
                  color: AppColors.legalNavy,
                  borderRadius: BorderRadius.circular(22),
                ),
                child: const Icon(
                  Icons.balance_rounded,
                  color: Colors.white,
                  size: 36,
                ),
              ),

              const SizedBox(height: 28),

              const Text(
                'How can Legal Lens help you?',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 30,
                  fontWeight: FontWeight.w700,
                  color: AppColors.legalNavy,
                ),
              ),

              const SizedBox(height: 12),

              const Text(
                'Ask questions, research legal topics, analyze documents, '
                'and explore legal information with AI assistance.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 15,
                  height: 1.6,
                  color: AppColors.textSecondary,
                ),
              ),

              const SizedBox(height: 38),

              Wrap(
                spacing: 14,
                runSpacing: 14,
                alignment: WrapAlignment.center,
                children: [
                  _SuggestionCard(
                    icon: Icons.search_rounded,
                    title: 'Research a legal topic',
                    description: 'Explore laws, concepts and legal principles.',
                    onTap: () {
                      onSuggestionSelected(
                        'Help me research an important legal topic.',
                      );
                    },
                  ),

                  _SuggestionCard(
                    icon: Icons.description_outlined,
                    title: 'Analyze a document',
                    description:
                        'Understand important clauses and legal information.',
                    onTap: () {
                      onSuggestionSelected('Help me analyze a legal document.');
                    },
                  ),

                  _SuggestionCard(
                    icon: Icons.gavel_outlined,
                    title: 'Explain a legal concept',
                    description: 'Get a simple explanation of a legal concept.',
                    onTap: () {
                      onSuggestionSelected(
                        'Explain an important legal concept in simple language.',
                      );
                    },
                  ),

                  _SuggestionCard(
                    icon: Icons.auto_awesome_rounded,
                    title: 'Advanced research',
                    description: 'Perform deeper AI-assisted legal research.',
                    onTap: () {
                      onSuggestionSelected(
                        'Help me perform advanced legal research on this topic.',
                      );
                    },
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _SuggestionCard extends StatelessWidget {
  const _SuggestionCard({
    required this.icon,
    required this.title,
    required this.description,
    required this.onTap,
  });

  final IconData icon;
  final String title;
  final String description;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 390,
      child: Material(
        color: AppColors.workspace,
        borderRadius: BorderRadius.circular(16),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(16),
          hoverColor: AppColors.hoverConversation,
          child: Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppColors.sidebarBorder),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    color: AppColors.legalNavyLight,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(icon, color: AppColors.legalNavy, size: 22),
                ),

                const SizedBox(width: 15),

                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: const TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.w700,
                          color: AppColors.textPrimary,
                        ),
                      ),

                      const SizedBox(height: 6),

                      Text(
                        description,
                        style: const TextStyle(
                          fontSize: 13,
                          height: 1.45,
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
