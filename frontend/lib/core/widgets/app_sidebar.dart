import 'package:flutter/material.dart';

class AppSidebar extends StatelessWidget {
  const AppSidebar({
    super.key,
    required this.selectedIndex,
    required this.onItemSelected,
  });

  final int selectedIndex;
  final ValueChanged<int> onItemSelected;

  static const double width = 260;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      width: width,
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border(right: BorderSide(color: Colors.grey.shade200)),
      ),
      child: Column(
        children: [
          const SizedBox(height: 24),

          // Brand
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Row(
              children: [
                Container(
                  width: 42,
                  height: 42,
                  decoration: BoxDecoration(
                    color: theme.colorScheme.primary,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.balance_rounded, color: Colors.white),
                ),
                const SizedBox(width: 12),
                const Expanded(
                  child: Text(
                    'LegalLens',
                    style: TextStyle(fontSize: 21, fontWeight: FontWeight.w700),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 32),

          _SidebarItem(
            icon: Icons.grid_view_rounded,
            label: 'Dashboard',
            selected: selectedIndex == 0,
            onTap: () => onItemSelected(0),
          ),

          _SidebarItem(
            icon: Icons.auto_awesome_rounded,
            label: 'AI Assistant',
            selected: selectedIndex == 1,
            onTap: () => onItemSelected(1),
          ),

          _SidebarItem(
            icon: Icons.description_outlined,
            label: 'Documents',
            selected: selectedIndex == 2,
            onTap: () => onItemSelected(2),
          ),

          _SidebarItem(
            icon: Icons.history_rounded,
            label: 'History',
            selected: selectedIndex == 3,
            onTap: () => onItemSelected(3),
          ),

          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 24, vertical: 20),
            child: Divider(),
          ),

          _SidebarItem(
            icon: Icons.bar_chart_rounded,
            label: 'Analytics',
            selected: selectedIndex == 4,
            onTap: () => onItemSelected(4),
          ),

          const Spacer(),

          const Divider(),

          _SidebarItem(
            icon: Icons.settings_outlined,
            label: 'Settings',
            selected: selectedIndex == 5,
            onTap: () => onItemSelected(5),
          ),

          const SizedBox(height: 16),
        ],
      ),
    );
  }
}

class _SidebarItem extends StatelessWidget {
  const _SidebarItem({
    required this.icon,
    required this.label,
    required this.selected,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 3),
      child: Material(
        color: selected
            ? theme.colorScheme.primary.withValues(alpha: 0.10)
            : Colors.transparent,
        borderRadius: BorderRadius.circular(10),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(10),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 13),
            child: Row(
              children: [
                Icon(
                  icon,
                  size: 21,
                  color: selected
                      ? theme.colorScheme.primary
                      : Colors.grey.shade600,
                ),
                const SizedBox(width: 14),
                Text(
                  label,
                  style: TextStyle(
                    fontWeight: selected ? FontWeight.w600 : FontWeight.w500,
                    color: selected
                        ? theme.colorScheme.primary
                        : Colors.grey.shade700,
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
