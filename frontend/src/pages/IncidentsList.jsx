/**
 * Incidents List Page
 * Entry point - shows all incidents
 * Calm, minimal, non-distracting
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import blackboxAPI from '../services/api';

const IncidentsList = () => {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const navigate = useNavigate();

  useEffect(() => {
    loadIncidents();
  }, [filter]);

  const loadIncidents = async () => {
    try {
      setLoading(true);
      const params = filter !== 'all' ? { status: filter } : {};
      const data = await blackboxAPI.getIncidents(params);
      setIncidents(data);
    } catch (error) {
      console.error('Failed to load incidents:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'UTC',
      timeZoneName: 'short'
    });
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return '#d32f2f';
      case 'medium': return '#f57c00';
      default: return '#616161';
    }
  };

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>BLACKBOX</h1>
        <p style={styles.subtitle}>Incident Reasoning Platform</p>
      </header>

      <div style={styles.controls}>
        <div style={styles.filterGroup}>
          <button
            style={{...styles.filterButton, ...(filter === 'all' ? styles.activeFilter : {})}}
            onClick={() => setFilter('all')}
          >
            All
          </button>
          <button
            style={{...styles.filterButton, ...(filter === 'open' ? styles.activeFilter : {})}}
            onClick={() => setFilter('open')}
          >
            Open
          </button>
          <button
            style={{...styles.filterButton, ...(filter === 'resolved' ? styles.activeFilter : {})}}
            onClick={() => setFilter('resolved')}
          >
            Resolved
          </button>
        </div>
      </div>

      {loading ? (
        <div style={styles.loading}>Loading incidents...</div>
      ) : incidents.length === 0 ? (
        <div style={styles.empty}>No incidents found</div>
      ) : (
        <div style={styles.incidentsList}>
          {incidents.map((incident) => (
            <div
              key={incident.id}
              style={styles.incidentCard}
              onClick={() => navigate(`/incidents/${incident.id}`)}
            >
              <div style={styles.incidentHeader}>
                <span style={styles.incidentId}>#{incident.id}</span>
                <span
                  style={{
                    ...styles.severityBadge,
                    backgroundColor: getSeverityColor(incident.severity)
                  }}
                >
                  {incident.severity || 'unknown'}
                </span>
                <span style={styles.statusBadge}>
                  {incident.status}
                </span>
              </div>

              <div style={styles.incidentInfo}>
                <div style={styles.service}>{incident.primary_service}</div>
                <div style={styles.environment}>{incident.environment}</div>
              </div>

              <div style={styles.incidentTime}>
                Started: {formatTime(incident.start_time)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '40px 20px',
  },
  header: {
    marginBottom: '40px',
    borderBottom: '1px solid #e0e0e0',
    paddingBottom: '20px',
  },
  title: {
    fontSize: '32px',
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: '8px',
  },
  subtitle: {
    fontSize: '16px',
    color: '#666',
    fontWeight: '400',
  },
  controls: {
    marginBottom: '30px',
  },
  filterGroup: {
    display: 'flex',
    gap: '10px',
  },
  filterButton: {
    padding: '8px 16px',
    border: '1px solid #e0e0e0',
    backgroundColor: '#fff',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
    color: '#666',
    transition: 'all 0.2s',
  },
  activeFilter: {
    backgroundColor: '#1a1a1a',
    color: '#fff',
    borderColor: '#1a1a1a',
  },
  loading: {
    textAlign: 'center',
    padding: '60px 20px',
    color: '#666',
    fontSize: '16px',
  },
  empty: {
    textAlign: 'center',
    padding: '60px 20px',
    color: '#999',
    fontSize: '16px',
  },
  incidentsList: {
    display: 'grid',
    gap: '16px',
  },
  incidentCard: {
    backgroundColor: '#fff',
    border: '1px solid #e0e0e0',
    borderRadius: '6px',
    padding: '20px',
    cursor: 'pointer',
    transition: 'all 0.2s',
    ':hover': {
      borderColor: '#1a1a1a',
    },
  },
  incidentHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '12px',
  },
  incidentId: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#1a1a1a',
  },
  severityBadge: {
    padding: '4px 10px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: '500',
    color: '#fff',
  },
  statusBadge: {
    padding: '4px 10px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: '500',
    backgroundColor: '#f5f5f5',
    color: '#666',
    textTransform: 'uppercase',
  },
  incidentInfo: {
    display: 'flex',
    gap: '12px',
    marginBottom: '12px',
  },
  service: {
    fontSize: '16px',
    fontWeight: '500',
    color: '#1a1a1a',
  },
  environment: {
    fontSize: '14px',
    color: '#666',
    padding: '2px 8px',
    backgroundColor: '#f5f5f5',
    borderRadius: '4px',
  },
  incidentTime: {
    fontSize: '13px',
    color: '#999',
  },
};

export default IncidentsList;
