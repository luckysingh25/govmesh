import {
  LayoutDashboard,
  FileText,
  Activity,
  Server,
  GitMerge,
  BrainCircuit,
  ShieldCheck,
  History,
  HeartPulse
} from 'lucide-react';

export const NAVIGATION_CONFIG = [
  {
    title: 'CITIZEN SERVICES',
    items: [
      {
        path: '/',
        label: 'Dashboard',
        pageTitle: 'Dashboard Overview',
        description: 'Unified command center & real-time federation overview',
        icon: LayoutDashboard,
        roles: ['admin', 'data_steward', 'citizen']
      },
      {
        path: '/service-request',
        label: 'Service Request',
        pageTitle: 'Service Request',
        description: 'Cross-departmental citizen service execution',
        icon: FileText,
        roles: ['citizen', 'admin']
      },
      {
        path: '/tracking',
        label: 'Application Tracking',
        pageTitle: 'Application Tracking',
        description: 'End-to-end execution status & transaction traces',
        icon: Activity,
        roles: ['citizen', 'admin', 'data_steward']
      },
      {
        path: '/consent',
        label: 'Consent Ledger',
        pageTitle: 'Consent Management (DPDP)',
        description: 'Digital Personal Data Protection statutory gate',
        icon: ShieldCheck,
        roles: ['citizen', 'admin']
      }
    ]
  },
  {
    title: 'DATA MESH & GOVERNANCE',
    items: [
      {
        path: '/intelligence',
        label: 'Schema Intelligence',
        pageTitle: 'Schema Intelligence',
        description: 'Autonomous schema evolution, field mapping & governance',
        icon: BrainCircuit,
        roles: ['admin', 'data_steward']
      },
      {
        path: '/systems',
        label: 'Connected Systems',
        pageTitle: 'Connected Systems',
        description: 'Departmental registries & legacy protocol adapters',
        icon: Server,
        roles: ['admin', 'data_steward']
      },
      {
        path: '/audit',
        label: 'Audit Ledger',
        pageTitle: 'Audit Ledger',
        description: 'Cryptographically sealed immutable compliance trail',
        icon: History,
        roles: ['admin', 'data_steward']
      }
    ]
  },
  {
    title: 'OPERATIONS & TELEMETRY',
    items: [
      {
        path: '/workflow',
        label: 'Workflow Orchestrator',
        pageTitle: 'Workflow Orchestration',
        description: 'Distributed choreography, aggregation & rollback engine',
        icon: GitMerge,
        roles: ['admin']
      },
      {
        path: '/health',
        label: 'System Health',
        pageTitle: 'System Health & Telemetry',
        description: 'Node status, latency metrics & circuit breaker telemetry',
        icon: HeartPulse,
        roles: ['admin']
      }
    ]
  }
];

export const getPageMeta = (pathname) => {
  for (const section of NAVIGATION_CONFIG) {
    for (const item of section.items) {
      if (item.path === pathname) {
        return {
          title: item.pageTitle,
          label: item.label,
          description: item.description,
          icon: item.icon
        };
      }
    }
  }

  // Fallback for dynamic or sub-routes
  const formatted = pathname.substring(1)
    .split('/')
    .filter(Boolean)
    .map(seg => seg.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '))
    .join(' · ');

  return {
    title: formatted || 'Dashboard Overview',
    label: formatted || 'Dashboard',
    description: 'GovMesh Federated Platform'
  };
};
