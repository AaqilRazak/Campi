import React, { useState, useEffect } from 'react';
import googleCalendarService from '../services/google-calendar.service';

const CalendarManager = () => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadEvents();
    }, []);

    const loadEvents = async () => {
        try {
            const calendarEvents = await googleCalendarService.getEvents();
            setEvents(calendarEvents);
        } catch (error) {
            console.error('Error loading events:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="calendar-manager">
            <h2>Academic Calendar Events</h2>
            {loading ? (
                <div>Loading events...</div>
            ) : (
                <div className="events-list">
                    {events.map(event => (
                        <div key={event.id} className="event-card">
                            <h3>{event.title}</h3>
                            <p>Start: {event.startDate.toLocaleDateString()}</p>
                            <p>End: {event.endDate.toLocaleDateString()}</p>
                            {event.description && (
                                <p className="description">{event.description}</p>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default CalendarManager; 