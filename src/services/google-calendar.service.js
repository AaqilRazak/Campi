import { google } from 'googleapis';

class GoogleCalendarService {
    constructor() {
        // Set up Google Calendar credentials
        this.auth = new google.auth.GoogleAuth({
            credentials: {
                client_email: process.env.GOOGLE_CLIENT_EMAIL,
                private_key: process.env.GOOGLE_PRIVATE_KEY.replace(/\\n/g, '\n'),
            },
            scopes: ['https://www.googleapis.com/auth/calendar.readonly'],
        });

        this.calendar = google.calendar({ version: 'v3', auth: this.auth });
        this.calendarId = process.env.GOOGLE_CALENDAR_ID; // Your calendar ID
    }

    async getEvents(timeMin = new Date()) {
        try {
            const response = await this.calendar.events.list({
                calendarId: this.calendarId,
                timeMin: timeMin.toISOString(),
                maxResults: 100,
                singleEvents: true,
                orderBy: 'startTime',
            });

            return response.data.items.map(event => ({
                title: event.summary,
                description: event.description,
                startDate: new Date(event.start.dateTime || event.start.date),
                endDate: new Date(event.end.dateTime || event.end.date),
                id: event.id
            }));
        } catch (error) {
            console.error('Error fetching calendar events:', error);
            throw error;
        }
    }

    async findEventsByKeywords(keywords) {
        const events = await this.getEvents();
        return events.filter(event => 
            keywords.some(keyword => 
                event.title.toLowerCase().includes(keyword.toLowerCase()) || 
                (event.description && event.description.toLowerCase().includes(keyword.toLowerCase()))
            )
        );
    }
}

export default new GoogleCalendarService(); 