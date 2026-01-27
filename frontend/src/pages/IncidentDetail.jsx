/**
 * Incident Detail Page
 * Primary analysis interface
 * Timeline is the hero
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import blackboxAPI from '../services/api';

const IncidentDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [incident, setIncident] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expandedEvents, setExpandedEvents] = useState(new Set());

  useEffect(() => {
    loadIncident();
  }, [id]);

  const loadIncident = async () => {
    try {
      setLoading(true);
      const data = await blackboxAPI.getIncident(id);
      setIncident(data);
    } catch (error) {
      console.error('Failed to load incident:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleResolve = async () => {
    try {
      await blackboxAPI.resolveIncident(id);
      loadIncident();
    } catch (error) {
      console.error('Failed to resolve incident:', error);
    }
  };

  const toggleEventExpansion = (eventId) => {
    setExpandedEvents(prev => {
      const newSet = new Set(prev);
      if (newSet.has(eventId)) {
        newSet.delete(eventId);
      } else {
        newSet.add(eventId);
      }
      return newSet;
    });
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      timeZone: 'UTC',
      timeZoneName: 'short'
    });
  };

  const getLevelColor = (level) => {
    switch (level) {
      case 'error': return '#d32f2f';
      case 'warning': return '#f57c00';
      case 'info': return '#1976d2';
      default: return '#616161';
    }
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loading}>Loading incident...</div>
      </div>
    );
  }

  if (!incident) {
    return (
      <div style={styles.container}>
        <div style={styles.error}>Incident not found</div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <button style={styles.backButton} onClick={() => navigate('/')}>
          ← Back to Incidents
        </button>
        <div style={styles.headerInfo}>
          <h1 style={styles.title}>Incident #{incident.id}</h1>
          {incident.status === 'open' && (
            <button style={styles.resolveButton} onClick={handleResolve}>
              Mark as Resolved
            </button>
          )}
        </div>
      </header>

      {/* Root Cause Summary */}
      <section style={styles.summarySection}>
        <h2 style={styles.sectionTitle}>Root Cause Summary</h2>
        <div style={styles.summaryBox}>
          <p style={styles.summaryText}>{incident.root_cause_summary}</p>
        </div>
        <div style={styles.metadata}>
          <span>Service: <strong>{incident.primary_service}</strong></span>
          <span>Environment: <strong>{incident.environment}</strong></span>
          <span>Events: <strong>{incident.event_count}</strong></span>
          <span>Severity: <strong>{incident.severity}</strong></span>
        </div>
      </section>

      {/* Timeline - The Hero */}
      <section style={styles.timelineSection}>
        <h2 style={styles.sectionTitle}>Timeline</h2>
        <p style={styles.timelineDescription}>
          Events in strict chronological order. Click to expand details.
        </p>

        <div style={styles.timeline}>
          {incident.timeline.map((event, index) => (
            <div key={event.id} style={styles.timelineEvent}>
              <div style={styles.timelineMarker}>
                <div
                  style={{
                    ...styles.markerDot,
                    backgroundColor: getLevelColor(event.level)
                  }}
                />
                {index < incident.timeline.length - 1 && (
                  <div style={styles.markerLine} />
                )}
              </div>

              <div style={styles.timelineContent}>
                <div
                  style={styles.eventHeader}
                  onClick={() => toggleEventExpansion(event.id)}
                >
                  <div style={styles.eventHeaderLeft}>
                    <span style={styles.eventTime}>
                      {formatTime(event.timestamp)}
                    </span>
                    <span
                      style={{
                        ...styles.levelBadge,
                        backgroundColor: getLevelColor(event.level)
                      }}
                    >
                      {event.level}
                    </span>
                    <span style={styles.serviceName}>{event.service}</span>
                  </div>
                  <span style={styles.expandIcon}>
                    {expandedEvents.has(event.id) ? '−' : '+'}
                  </span>
                </div>

                <div style={styles.eventMessage}>{event.message}</div>

                {expandedEvents.has(event.id) && (
                  <div style={styles.eventDetails}>
                    <div style={styles.detailRow}>
                      <span style={styles.detailLabel}>Event ID:</span>
                      <span style={styles.detailValue}>{event.id}</span>
                    </div>
                    {event.request_id && (
                      <div style={styles.detailRow}>
                        <span style={styles.detailLabel}>Request ID:</span>
                        <span style={styles.detailValue}>{event.request_id}</span>
                      </div>
                    )}
                    <div style={styles.detailRow}>
                      <span style={styles.detailLabel}>Correlation:</span>
                      <span style={styles.detailValue}>{event.correlation_reason}</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

const styles = {
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '40px 20px',
  },
  loading: {
    textAlign: 'center',
    padding: '60px 20px',
    color: '#666',
    fontSize: '16px',
  },
  error: {
    textAlign: 'center',
    padding: '60px 20px',
    color: '#d32f2f',
    fontSize: '16px',
  },
  header: {
    marginBottom: '40px',
  },
  backButton: {
    padding: '8px 16px',
    border: '1px solid #e0e0e0',
    backgroundColor: '#fff',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
    color: '#666',
    marginBottom: '20px',
  },
  headerInfo: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    fontSize: '32px',
    fontWeight: '600',
    color: '#1a1a1a',
  },
  resolveButton: {
    padding: '10px 20px',
    border: 'none',
    backgroundColor: '#1a1a1a',
    color: '#fff',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500',
  },
  summarySection: {
    marginBottom: '40px',
  },
  sectionTitle: {
    fontSize: '20px',
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: '16px',
  },
  summaryBox: {
    backgroundColor: '#fffbf0',
    border: '1px solid #ffe082',
    borderRadius: '6px',
    padding: '20px',
    marginBottom: '16px',
  },
  summaryText: {
    fontSize: '16px',
    lineHeight: '1.6',
    color: '#1a1a1a',
  },
  metadata: {
    display: 'flex',
    gap: '24px',
    fontSize: '14px',
    color: '#666',
  },
  timelineSection: {
    marginBottom: '40px',
  },
  timelineDescription: {
    fontSize: '14px',
    color: '#666',
    marginBottom: '24px',
  },
  timeline: {
    position: 'relative',
  },
  timelineEvent: {
    display: 'flex',
    gap: '16px',
    marginBottom: '8px',
  },
  timelineMarker: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    paddingTop: '6px',
  },
  markerDot: {
    width: '12px',
    height: '12px',
    borderRadius: '50%',
    flexShrink: 0,
  },
  markerLine: {
    width: '2px',
    flexGrow: 1,
    backgroundColor: '#e0e0e0',
    marginTop: '4px',
  },
  timelineContent: {
    flex: 1,
    marginBottom: '16px',
  },
  eventHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px 16px',
    backgroundColor: '#fff',
    border: '1px solid #e0e0e0',
    borderRadius: '6px 6px 0 0',
    cursor: 'pointer',
  },
  eventHeaderLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  eventTime: {
    fontSize: '13px',
    color: '#666',
    fontFamily: 'monospace',
  },
  levelBadge: {
    padding: '4px 8px',
    borderRadius: '12px',
    fontSize: '11px',
    fontWeight: '600',
    color: '#fff',
    textTransform: 'uppercase',
  },
  serviceName: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#1a1a1a',
  },
  expandIcon: {
    fontSize: '18px',
    color: '#666',
    fontWeight: '600',
  },
  eventMessage: {
    padding: '12px 16px',
    backgroundColor: '#fafafa',
    border: '1px solid #e0e0e0',
    borderTop: 'none',
    borderRadius: '0 0 6px 6px',
    fontSize: '14px',
    lineHeight: '1.5',
    color: '#333',
  },
  eventDetails: {
    padding: '12px 16px',
    backgroundColor: '#f5f5f5',
    border: '1px solid #e0e0e0',
    borderTop: 'none',
    borderRadius: '0 0 6px 6px',
    marginTop: '-6px',
  },
  detailRow: {
    display: 'flex',
    gap: '12px',
    marginBottom: '6px',
    fontSize: '13px',
  },
  detailLabel: {
    color: '#666',
    fontWeight: '500',
    minWidth: '120px',
  },
  detailValue: {
    color: '#1a1a1a',
    fontFamily: 'monospace',
  },
};

export default IncidentDetail;
