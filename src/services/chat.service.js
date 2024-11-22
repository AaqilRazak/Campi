import googleCalendarService from './google-calendar.service';

class ChatService {
    async handleCalendarQuery(userInput) {
        const keywords = this.extractKeywords(userInput);
        try {
            const relevantEvents = await googleCalendarService.findEventsByKeywords(keywords);
            
            if (relevantEvents.length > 0) {
                const eventResponses = relevantEvents.map(event => ({
                    title: event.title,
                    date: event.startDate.toLocaleDateString(),
                    description: event.description
                }));

                return this.formatCalendarResponse(eventResponses);
            }
            
            return "I couldn't find any calendar events matching your query.";
        } catch (error) {
            console.error('Error handling calendar query:', error);
            return "I'm having trouble accessing the calendar right now.";
        }
    }

    extractKeywords(userInput) {
        const commonKeywords = {
            'registration': ['register', 'registration', 'sign up'],
            'deadlines': ['deadline', 'due date', 'last day'],
            'finals': ['final', 'finals', 'exam'],
            'breaks': ['break', 'holiday', 'vacation']
        };

        return Object.values(commonKeywords).flat()
            .filter(keyword => userInput.toLowerCase().includes(keyword));
    }

    formatCalendarResponse(events) {
        if (events.length === 1) {
            const event = events[0];
            return `${event.title} is scheduled for ${event.date}. ${event.description || ''}`;
        }

        return 'Here are the relevant dates:\n' + 
            events.map(event => `- ${event.title}: ${event.date}`).join('\n');
    }
}

export default new ChatService(); 