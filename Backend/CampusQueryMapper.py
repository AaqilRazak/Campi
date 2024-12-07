from typing import Optional
from datetime import datetime, timedelta
import re
import logging

class CampusDemoQueryMapper:
    def __init__(self, db_connection):
        self.db = db_connection
        # Adjusted patterns to ensure correct capturing groups
        self.patterns = {
            # Quick Info Queries
            r"what's happening(?: right)? now\??": self._get_current_happenings,
            r"what's going on this week\??": self.get_events_this_week,
            r"what buildings are open(?: right now)?(?: that I can study in)?\??": self.get_open_buildings_to_study,
            
            # Social/Fun Queries
            r"what fun events are happening today\??": self._get_fun_events,
            r"what student organizations are active this semester\??": self._get_student_organizations,
            r"where (?:can|do) (?:students|people) hang out\??": self._get_social_spots,
            r"what's fun (?:to do |happening )?(today|tonight|this weekend)\??": self._get_entertainment,
            r"any free food (today|now|happening)\??": self._get_free_food_events,
            r"where(?:'s| is) the best (?:place to |spot for )?study\??": self._get_top_study_spots,
            
            # Time-Sensitive Queries
            r"what's open (?:(late)|after (\d{1,2})(am|pm))\??": self._get_late_night_options,
            r"where can I get food (?:(late)|after (\d{1,2})(am|pm))\??": self._get_late_food_options,
            r"is (.+?) busy right now\??": self._get_location_busyness,
            r"what's the best time to visit (.+?)\??": self._get_quiet_times,
            
            # Emergency/Urgent Queries
            r"I need a (quiet|silent) place (?:to study|right now)\??": self._get_quiet_study_spots,
            r"where's the nearest (bathroom|printer|water fountain)\??": self._get_nearest_amenity,
            r"(?:help|i need) (?:to print|printing)\??": self._get_printing_help,
            r"where can I charge my (phone|laptop)\??": self._get_charging_spots,
            
            # Weather-Based Queries
            r"where can I study (inside|outside)\??": self._get_weather_based_spots,
            r"(?:is there|any) indoor seating (?:in|at) (.+?)\??": self._get_indoor_seating,
            r"where can I stay warm|any cozy spots\??": self._get_cozy_spots,
            
            # Event Discovery
            r"anything free (today|this week)\??": self._get_free_events,
            r"what clubs are meeting (today|this week)\??": self._get_club_meetings,
            r"any (?:good |interesting )?events (today|tonight|this week)\??": self._get_highlighted_events,
            r"what should I do (today|tonight|this weekend)\??": self._get_personalized_suggestions,
            
            # Specific Time Queries
            r"what's good for (breakfast|lunch|dinner)\??": self._get_meal_recommendations,
            r"what's happening (?:at|around) (\d{1,2})(am|pm)\??": self._get_events_by_time,
            
            # Group Activity Queries
            r"where can I study with a group\??": self._get_group_study_spots,
            r"where can I have (a meeting|team practice)\??": self._get_meeting_spaces,
            r"good places to meet friends\??": self._get_meetup_spots
        }

    async def match_and_execute(self, user_input: str) -> str:
        """Match user input against patterns and execute corresponding handler"""
        try:
            logging.info(f"Attempting to match input: {user_input}")
                
            # Convert input to lowercase for matching
            user_input = user_input.lower().strip()
                
            # Try each pattern
            for pattern, handler in self.patterns.items():
                    if re.match(pattern, user_input):
                        logging.info(f"Matched pattern: {pattern}")
                        return await handler()
                
                # If no pattern matches
            logging.info("No pattern matched")
            return "I'm not sure how to help with that question. Could you try rephrasing it?"
                
        except Exception as e:
                logging.error(f"Error in match_and_execute: {str(e)}")
                return "Sorry, I encountered an error processing your request."

    # Current Happenings Handler - Great Demo Opener
    async def _get_current_happenings(self) -> str:
        try:
            # Get the current datetime
            current_datetime = datetime.now()
            current_date = current_datetime.strftime('%Y-%m-%d')
            current_time = current_datetime.strftime('%H:%M:%S')

            # Query to get all events for today
            query = f"""
                SELECT e.EventName, e.EventDateTime, c.BuildingName, e.EventDescription
                FROM EventInformation e
                JOIN CampusInformation c ON e.EventLocationID = c.BuildingID
                WHERE strftime('%Y-%m-%d', e.EventDateTime) = '{current_date}'
                ORDER BY e.EventDateTime
            """
            
            # Log the constructed query
            logging.info(f"Executing query:\n{query}")

            async with self.db.execute(query) as cursor:
                events = await cursor.fetchall()

            # If no events found, try a broader query to debug
            if not events:
                debug_query = f"""
                    SELECT e.EventName, e.EventDateTime, c.BuildingName
                    FROM EventInformation e
                    JOIN CampusInformation c ON e.EventLocationID = c.BuildingID
                    WHERE strftime('%Y-%m-%d', e.EventDateTime) = '{current_date}'
                    ORDER BY e.EventDateTime
                """
                async with self.db.execute(debug_query) as cursor:
                    debug_events = await cursor.fetchall()
                    logging.info(f"Debug - All events today: {debug_events}")

            logging.info(f"Number of events fetched: {len(events)}")

            response_parts = []

            if events:
                response_parts.append(f"🎯 **All Events Today (Current Time: {current_time}):**")
                for event in events:
                    event_name, event_datetime, building_name, event_description = event
                    try:
                        event_time = datetime.strptime(event_datetime, '%Y-%m-%d %H:%M:%S').strftime('%I:%M %p')
                    except ValueError:
                        event_time = event_datetime

                    response_parts.append(
                        f"• **{event_name}** at **{building_name}**\n  🕒 {event_time}\n  {event_description}"
                    )
            else:
                response_parts.append("🎉 **No events scheduled for today.**\nYou can ask me about upcoming events or specific places on campus!")

            return "\n".join(response_parts)

        except Exception as e:
            logging.error(f"Error in _get_current_happenings: {str(e)}")
            logging.error(f"Exception type: {type(e)}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")
            return "😕 I couldn't fetch the current happenings. Please try again later or ask about specific events!"
        

    async def get_events_this_week(self) -> str:
        try:
            # Get current datetime and end of week
            current_datetime = datetime.now()
            end_of_week = current_datetime + timedelta(days=7)
            
            # Format dates for query
            current_date = current_datetime.strftime('%Y-%m-%d')
            end_date = end_of_week.strftime('%Y-%m-%d')

            # Query for weekly events
            query = f"""
                SELECT e.EventName, e.EventDateTime, c.BuildingName, e.EventDescription
                FROM EventInformation e
                JOIN CampusInformation c ON e.EventLocationID = c.BuildingID
                WHERE date(e.EventDateTime) BETWEEN '{current_date}' AND '{end_date}'
                ORDER BY e.EventDateTime
            """
            
            logging.info(f"Weekly Events Query: {query}")

            async with self.db.execute(query) as cursor:
                events = await cursor.fetchall()

            logging.info(f"Weekly events found: {len(events)}")

            response_parts = []

            if events:
                response_parts.append(f"🗓️ **Upcoming Events ({current_date} to {end_date}):**")
                for event in events:
                    event_name, event_datetime, building_name, event_description = event
                    try:
                        # Format date to include day of week and time
                        event_time = datetime.strptime(event_datetime, '%Y-%m-%d %H:%M:%S').strftime('%A, %B %d at %I:%M %p')
                        response_parts.append(
                            f"• **{event_name}** at **{building_name}**\n  🕒 {event_time}\n  {event_description}"
                        )
                    except ValueError as e:
                        logging.error(f"DateTime parsing error: {e} for datetime: {event_datetime}")
                        continue

            else:
                response_parts.append("🎉 **No events scheduled for this week.**\nYou can ask me about upcoming events or specific places on campus!")

            return "\n".join(response_parts)

        except Exception as e:
            logging.error(f"Error in get_events_this_week: {str(e)}")
            logging.error(f"Exception type: {type(e)}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")
            return "😕 I couldn't fetch the events for this week. Please try again later!"

    # New Handler for Open Buildings to Study
    async def get_open_buildings_to_study(self) -> str:
        try:
            # Get current time
            current_time = datetime.now().strftime("%H:%M")
            
            # Debug log the current time
            logging.info(f"Current time: {current_time}")
            
            # First get all study locations to debug
            debug_query = f"""
                SELECT BuildingName, Description, BuildingHours
                FROM CampusInformation 
                WHERE (
                    LOWER(Description) LIKE '%study%'
                    OR LOWER(Description) LIKE '%library%'
                    OR LOWER(Description) LIKE '%study area%'
                    OR LOWER(Description) LIKE '%quiet area%'
                )
            """
            
            async with self.db.execute(debug_query) as cursor:
                all_study_places = await cursor.fetchall()
            logging.info(f"Total study places found (before time filter): {len(all_study_places)}")
            
            # Modified query to handle time ranges better
            query = f"""
                SELECT BuildingName, Description, BuildingHours
                FROM CampusInformation 
                WHERE (
                    LOWER(Description) LIKE '%study%'
                    OR LOWER(Description) LIKE '%library%'
                    OR LOWER(Description) LIKE '%study area%'
                    OR LOWER(Description) LIKE '%quiet area%'
                )
                AND (
                    BuildingHours = '24/7'
                    OR BuildingHours = '00:00-23:59'
                    OR (
                        SUBSTR(BuildingHours, 1, INSTR(BuildingHours, '-') - 1) <= '{current_time}'
                        AND SUBSTR(BuildingHours, INSTR(BuildingHours, '-') + 1) >= '{current_time}'
                    )
                )
                ORDER BY BuildingName
            """
            
            logging.info(f"Executing query:\n{query}")

            async with self.db.execute(query) as cursor:
                buildings = await cursor.fetchall()

            logging.info(f"Number of open buildings fetched: {len(buildings)}")
            
            # Debug log all returned buildings
            for building in buildings:
                logging.info(f"Found open building: {building}")

            response_parts = []

            if buildings:
                response_parts.append(f"📚 **Places to Study Now (Current Time: {current_time}):**")
                for building in buildings:
                    building_name, description, building_hours = building
                    response_parts.append(
                        f"• **{building_name}**\n  📍 {description}\n  🕒 Hours: {building_hours}"
                    )
            else:
                response_parts.append("😴 **No study spaces are currently open.**\nTry asking about locations that open later!")

            return "\n".join(response_parts)

        except Exception as e:
            logging.error(f"Error in get_open_buildings_to_study: {str(e)}")
            logging.error(f"Exception type: {type(e)}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")
            return "😕 I couldn't find study space information right now. Please try again later!"
    

    async def _get_recommended_spots(self, activity: str) -> str:
        try:
            async with self.db.execute('''
                SELECT BuildingName, Description, BuildingHours
                FROM CampusInformation
                WHERE LOWER(Description) LIKE ?
                ORDER BY BuildingName
                LIMIT 5
            ''', (f'%{activity.lower()}%',)) as cursor:
                spots = await cursor.fetchall()

            if not spots:
                return f"I couldn't find any recommended spots for {activity}. Try a different activity!"

            response = f"🔍 **Recommended places for {activity}:**\n\n"
            for spot in spots:
                response += f"• **{spot[0]}**\n  {spot[1]}\n  🕒 Hours: {spot[2]}\n"

            return response
        except Exception as e:
            logging.error(f"Error in _get_recommended_spots: {str(e)}")
            return "I couldn't find recommended spots for that activity. Please try again later."

    # Social/Fun Handlers
    async def _get_social_spots(self, _, group_type: str) -> str:
        try:
            async with self.db.execute('''
                SELECT BuildingName, Description, BuildingHours
                FROM CampusInformation 
                WHERE LOWER(Description) LIKE '%hang out%'
                OR LOWER(Description) LIKE '%social%'
                ORDER BY BuildingName
                LIMIT 5
            ''') as cursor:
                spots = await cursor.fetchall()

            if not spots:
                return "I couldn't find any social spots right now. Try asking about different activities!"

            response = "🎉 **Popular social spots:**\n\n"
            for spot in spots:
                response += f"• **{spot[0]}**\n  {spot[1]}\n  🕒 Hours: {spot[2]}\n"

            return response
        except Exception as e:
            logging.error(f"Error in _get_social_spots: {str(e)}")
            return "I couldn't retrieve social spots at the moment. Please try again later."

    async def _get_entertainment(self, _, timeframe: str) -> str:
        try:
            time_clauses = {
                'today': "DATE(e.EventDateTime) = DATE('now')",
                'tonight': "DATE(e.EventDateTime) = DATE('now') AND TIME(e.EventDateTime) >= '17:00'",
                'this weekend': "strftime('%w', e.EventDateTime) IN ('5','6') AND DATE(e.EventDateTime) >= DATE('now')"
            }

            clause = time_clauses.get(timeframe.lower(), "DATE(e.EventDateTime) = DATE('now')")

            async with self.db.execute(f'''
                SELECT e.EventName, e.EventDateTime, c.BuildingName,
                       e.EventDescription, e.OrganizerContact
                FROM EventInformation e
                JOIN CampusInformation c ON e.EventLocationID = c.BuildingID
                WHERE {clause}
                AND (
                    LOWER(e.EventDescription) LIKE '%fun%'
                    OR LOWER(e.EventDescription) LIKE '%social%'
                    OR LOWER(e.EventDescription) LIKE '%entertainment%'
                    OR LOWER(e.EventDescription) LIKE '%game%'
                    OR LOWER(e.EventDescription) LIKE '%music%'
                    OR LOWER(e.EventDescription) LIKE '%party%'
                )
                ORDER BY e.EventDateTime
                LIMIT 5
            ''') as cursor:
                events = await cursor.fetchall()

            if not events:
                return f"No entertainment events found {timeframe}. Try asking about another time!"

            response = f"🎉 **Fun stuff happening {timeframe}:**\n\n"
            for event in events:
                event_time = datetime.strptime(event[1], '%Y-%m-%d %H:%M:%S').strftime('%I:%M %p')
                response += (f"• **{event[0]}** at **{event[2]}**\n"
                             f"  🕒 When: {event_time}\n"
                             f"  {event[3]}\n"
                             f"  📞 Contact: {event[4]}\n")
            
            return response
        except Exception as e:
            logging.error(f"Error in _get_entertainment: {str(e)}")
            return "I couldn't fetch entertainment options at the moment. Please try again later."

    async def _get_free_food_events(self, _, timeframe: str) -> str:
        try:
            time_clause = "DATE(e.EventDateTime) = DATE('now')"
            if timeframe.lower() in ["now", "happening"]:
                time_clause = "DATE(e.EventDateTime) = DATE('now')"
            elif timeframe.lower() == "today":
                time_clause = "DATE(e.EventDateTime) = DATE('now')"
            elif timeframe.lower() == "happening":
                time_clause = "DATE(e.EventDateTime) = DATE('now')"

            async with self.db.execute('''
                SELECT e.EventName, e.EventDateTime, c.BuildingName,
                       e.EventDescription, e.OrganizerContact
                FROM EventInformation e
                JOIN CampusInformation c ON e.EventLocationID = c.BuildingID
                WHERE {time_clause}
                AND (
                    LOWER(e.EventDescription) LIKE '%free food%'
                    OR LOWER(e.EventDescription) LIKE '%free pizza%'
                    OR LOWER(e.EventDescription) LIKE '%refreshments%'
                    OR LOWER(e.EventDescription) LIKE '%snacks%'
                )
                ORDER BY e.EventDateTime
                LIMIT 3
            '''.format(time_clause=time_clause)) as cursor:
                events = await cursor.fetchall()

            if not events:
                return "No free food events found today. Try asking about events later this week!"

            response = "🍕 **Events with free food today:**\n\n"
            for event in events:
                event_time = datetime.strptime(event[1], '%Y-%m-%d %H:%M:%S').strftime('%I:%M %p')
                response += (f"• **{event[0]}** at **{event[2]}**\n"
                             f"  🕒 When: {event_time}\n"
                             f"  {event[3]}\n"
                             f"  📞 Contact: {event[4]}\n")
            
            return response
        except Exception as e:
            logging.error(f"Error in _get_free_food_events: {str(e)}")
            return "I couldn't fetch free food events at the moment. Please try again later."

    async def _get_top_study_spots(self) -> str:
        try:
            current_time = datetime.now()
            
            async with self.db.execute('''
                SELECT BuildingName, Description, BuildingHours
                FROM CampusInformation 
                WHERE (
                    LOWER(Description) LIKE '%study%'
                    OR LOWER(Description) LIKE '%quiet%'
                    OR LOWER(Description) LIKE '%library%'
                )
                AND BuildingHours LIKE ?
                ORDER BY
                    CASE
                        WHEN LOWER(Description) LIKE '%quiet%' THEN 1
                        WHEN LOWER(Description) LIKE '%library%' THEN 2
                        ELSE 3
                    END,
                    BuildingName
                LIMIT 4
            ''', (f'%{current_time.strftime("%H:%M")}%',)) as cursor:
                spots = await cursor.fetchall()

            if not spots:
                return "I couldn't find any study spots open right now. Try asking about specific times!"

            response = "📚 **Top study spots open now:**\n\n"
            for spot in spots:
                response += (f"• **{spot[0]}**\n"
                            f"  {spot[1]}\n"
                            f"  🕒 Hours: {spot[2]}\n")
            
            response += "\n💡 Pro tip: Looking for a quiet spot? Try asking 'I need a quiet place to study!'"
            return response
        except Exception as e:
            logging.error(f"Error in _get_top_study_spots: {str(e)}")
            return "I couldn't retrieve study spots at the moment. Please try again later."

    async def _get_late_night_options(self, option: str) -> str:
        try:
            current_time = datetime.now()

            if "late" in option.lower():
                time_range = "21:00:00"  # Assuming late night starts at 9 PM
            else:
                match = re.search(r'after (\d{1,2})(am|pm)', option.lower())
                if match:
                    hour = int(match.group(1))
                    period = match.group(2)
                    if period == "pm" and hour != 12:
                        hour += 12
                    time_range = f"{hour:02}:00:00"
                else:
                    time_range = "21:00:00"

            async with self.db.execute('''
                SELECT BuildingName, Description, BuildingHours
                FROM CampusInformation 
                WHERE BuildingHours LIKE ?
                ORDER BY BuildingName
                LIMIT 5
            ''', (f'%{time_range}%',)) as cursor:
                spots = await cursor.fetchall()

            if not spots:
                return "I couldn't find any places open late right now. Try asking about different times!"

            response = "🌙 **Places open late:**\n\n"
            for spot in spots:
                response += f"• **{spot[0]}**\n  {spot[1]}\n  🕒 Hours: {spot[2]}\n"

            return response
        except Exception as e:
            logging.error(f"Error in _get_late_night_options: {str(e)}")
            return "I couldn't retrieve late night options at the moment. Please try again later."

    async def _get_late_food_options(self, option: str) -> str:
        try:
            current_time = datetime.now()

            if "late" in option.lower():
                time_range = "21:00:00"  # Assuming late night starts at 9 PM
            else:
                match = re.search(r'after (\d{1,2})(am|pm)', option.lower())
                if match:
                    hour = int(match.group(1))
                    period = match.group(2)
                    if period == "pm" and hour != 12:
                        hour += 12
                    time_range = f"{hour:02}:00:00"
                else:
                    time_range = "21:00:00"

            async with self.db.execute('''
                SELECT BuildingName, Description, BuildingHours
                FROM CampusInformation 
                WHERE (LOWER(Description) LIKE '%food%'
                OR LOWER(Description) LIKE '%dining%'
                OR LOWER(Description) LIKE '%restaurant%')
                AND BuildingHours LIKE ?
                ORDER BY BuildingName
                LIMIT 5
            ''', (f'%{time_range}%',)) as cursor:
                food_spots = await cursor.fetchall()

            if not food_spots:
                return "I couldn't find any food places open late right now. Try asking about different times!"

            response = "🌙 **Food places open late:**\n\n"
            for spot in food_spots:
                response += f"• **{spot[0]}**\n  {spot[1]}\n  🕒 Hours: {spot[2]}\n"

            return response
        except Exception as e:
            logging.error(f"Error in _get_late_food_options: {str(e)}")
            return "I couldn't retrieve late food options at the moment. Please try again later."

    async def _get_location_busyness(self, location: str) -> str:
        try:
            # Assuming there's a table or method to get current busyness
            async with self.db.execute('''
                SELECT BusynessLevel, LastUpdated
                FROM LocationBusyness
                WHERE LOWER(LocationName) = ?
            ''', (location.lower(),)) as cursor:
                result = await cursor.fetchone()

            if not result:
                return f"I couldn't find busyness information for {location}. Please try another location!"

            busyness_level, last_updated = result
            last_updated_time = datetime.strptime(last_updated, '%Y-%m-%d %H:%M:%S')

            if datetime.now() - last_updated_time > timedelta(minutes=30):
                return f"I don't have up-to-date information on {location}. Please check back later."

            response = f"📊 **Busyness at {location.title()}:**\n\n• **Current Level:** {busyness_level}\n• **Last Updated:** {last_updated_time.strftime('%I:%M %p')}"
            return response
        except Exception as e:
            logging.error(f"Error in _get_location_busyness: {str(e)}")
            return "I couldn't retrieve busyness information at the moment. Please try again later."

    async def _get_quiet_times(self, location: str) -> str:
        try:
            async with self.db.execute('''
                SELECT BestVisitTime, QuietLevel
                FROM LocationQuietTimes
                WHERE LOWER(LocationName) = ?
                ORDER BY QuietLevel DESC
                LIMIT 1
            ''', (location.lower(),)) as cursor:
                result = await cursor.fetchone()

            if not result:
                return f"I couldn't find quiet times information for {location}. Please try another location!"

            best_time, quiet_level = result
            response = f"🕒 **Best Time to Visit {location.title()}:**\n\n• **Time:** {best_time}\n• **Quiet Level:** {quiet_level}"
            return response
        except Exception as e:
            logging.error(f"Error in _get_quiet_times: {str(e)}")
            return "I couldn't retrieve quiet times information at the moment. Please try again later."

    # Emergency/Urgent Handlers
    async def _get_quiet_study_spots(self, adjective: str, purpose: str) -> str:
        try:
            async with self.db.execute('''
                SELECT BuildingName, Description, BuildingHours
                FROM CampusInformation 
                WHERE (
                    LOWER(Description) LIKE '%quiet%'
                    OR LOWER(Description) LIKE '%silent%'
                    OR LOWER(Description) LIKE '%library%'
                )
                AND BuildingHours LIKE ?
                ORDER BY BuildingName
                LIMIT 5
            ''', (f'%{datetime.now().strftime("%H:%M")}%',)) as cursor:
                spots = await cursor.fetchall()

            if not spots:
                return "I couldn't find any quiet study spots open right now. Try asking about specific times!"

            response = "🔇 **Quiet study spots available now:**\n\n"
            for spot in spots:
                response += f"• **{spot[0]}**\n  {spot[1]}\n  🕒 Hours: {spot[2]}\n"

            return response
        except Exception as e:
            logging.error(f"Error in _get_quiet_study_spots: {str(e)}")
            return "I couldn't retrieve quiet study spots at the moment. Please try again later."

    async def _get_nearest_amenity(self, _, amenity_type: str) -> str:
        try:
            amenity_keywords = {
                'bathroom': ['bathroom', 'restroom'],
                'printer': ['printer', 'printing'],
                'water fountain': ['water fountain', 'hydration station']
            }

            keywords = amenity_keywords.get(amenity_type.lower(), [amenity_type.lower()])
            query_conditions = " OR ".join([f"LOWER(Description) LIKE '%{kw}%'" for kw in keywords])

            async with self.db.execute(f'''
                SELECT BuildingName, Description, BuildingHours, BuildingLocation
                FROM CampusInformation 
                WHERE {query_conditions}
                ORDER BY BuildingName
                LIMIT 3
            ''') as cursor:
                amenities = await cursor.fetchall()

            if not amenities:
                return f"I couldn't find the nearest {amenity_type}. Please try a different amenity!"

            response = f"🚻 **Nearest {amenity_type.title()}:**\n\n"
            for amenity in amenities:
                response += f"• **{amenity[0]}**\n  {amenity[1]}\n  🕒 Hours: {amenity[2]}\n  📍 Location: {amenity[3]}\n"

            return response
        except Exception as e:
            logging.error(f"Error in _get_nearest_amenity: {str(e)}")
            return "I couldn't find the nearest amenity at the moment. Please try again later."

    async def _get_printing_help(self, _, action: str) -> str:
        try:
            async with self.db.execute('''
                SELECT ServiceName, Description, ContactInfo, OperatingHours
                FROM PrintingServices
                WHERE LOWER(ServiceName) LIKE '%print%'
                OR LOWER(ServiceName) LIKE '%printing%'
            ''') as cursor:
                services = await cursor.fetchall()

            if not services:
                return "I couldn't find any printing services available right now. Please try again later."

            response = "🖨️ **Printing Services Available:**\n\n"
            for service in services:
                response += f"• **{service[0]}**\n  {service[1]}\n  📞 Contact: {service[2]}\n  🕒 Hours: {service[3]}\n"

            return response
        except Exception as e:
            logging.error(f"Error in _get_printing_help: {str(e)}")
            return "I couldn't retrieve printing services information at the moment. Please try again later."

    async def _get_charging_spots(self, device: str) -> str:
        try:
            async with self.db.execute('''
                SELECT BuildingName, Description, BuildingHours
                FROM CampusInformation 
                WHERE LOWER(Description) LIKE '%charge%'
                OR LOWER(Description) LIKE '%power outlet%'
                ORDER BY BuildingName
                LIMIT 5
            ''') as cursor:
                chargers = await cursor.fetchall()

            if not chargers:
                return f"I couldn't find any places to charge your {device}. Please try asking about different locations!"

            response = f"🔌 **Places to charge your {device}:**\n\n"
            for charger in chargers:
                response += f"• **{charger[0]}**\n  {charger[1]}\n  🕒 Hours: {charger[2]}\n"

            return response
        except Exception as e:
            logging.error(f"Error in _get_charging_spots: {str(e)}")
            return "I couldn't find charging spots at the moment. Please try again later."

    # Weather-Based Recommendations - Nice Demo Touch
    async def _get_weather_based_spots(self, location_type: str) -> str:
        try:
            current_time = datetime.now()
            
            location_clause = "LOWER(Description) LIKE '%indoor%'" if location_type.lower() == "inside" else "LOWER(Description) LIKE '%outdoor%'"
            
            async with self.db.execute(f'''
                SELECT BuildingName, Description, BuildingHours
                FROM CampusInformation 
                WHERE {location_clause}
                AND BuildingHours LIKE ?
                ORDER BY BuildingName
                LIMIT 4
            ''', (f'%{current_time.strftime("%H:%M")}%',)) as cursor:
                spots = await cursor.fetchall()

            if not spots:
                return f"I couldn't find any {location_type} spots open right now. Try asking about specific times!"

            emoji = "🏢" if location_type.lower() == "inside" else "🌳"
            response = f"{emoji} **{location_type.capitalize()} spots open now:**\n\n"
            for spot in spots:
                response += f"• **{spot[0]}**\n  {spot[1]}\n  🕒 Hours: {spot[2]}\n"

            return response
        except Exception as e:
            logging.error(f"Error in _get_weather_based_spots: {str(e)}")
            return "I couldn't retrieve weather-based spots at the moment. Please try again later."

    async def _get_indoor_seating(self, _, location: str) -> str:
        try:
            async with self.db.execute('''
                SELECT BuildingName, Description, BuildingHours
                FROM CampusInformation 
                WHERE LOWER(Description) LIKE '%indoor seating%'
                AND LOWER(Description) LIKE ?
                ORDER BY BuildingName
                LIMIT 5
            ''', (f'%{location.lower()}%',)) as cursor:
                seats = await cursor.fetchall()

            if not seats:
                return f"I couldn't find any indoor seating in {location}. Please try a different area!"

            response = f"🪑 **Indoor seating available in {location.title()}:**\n\n"
            for seat in seats:
                response += f"• **{seat[0]}**\n  {seat[1]}\n  🕒 Hours: {seat[2]}\n"

            return response
        except Exception as e:
            logging.error(f"Error in _get_indoor_seating: {str(e)}")
            return "I couldn't find indoor seating at the moment. Please try again later."

    async def _get_cozy_spots(self) -> str:
        try:
            async with self.db.execute('''
                SELECT BuildingName, Description, BuildingHours
                FROM CampusInformation 
                WHERE LOWER(Description) LIKE '%cozy%'
                OR LOWER(Description) LIKE '%warm%'
                ORDER BY BuildingName
                LIMIT 5
            ''') as cursor:
                spots = await cursor.fetchall()

            if not spots:
                return "I couldn't find any cozy spots open right now. Try asking about different locations or times!"

            response = "🔥 **Cozy spots open now:**\n\n"
            for spot in spots:
                response += f"• **{spot[0]}**\n  {spot[1]}\n  🕒 Hours: {spot[2]}\n"

            return response
        except Exception as e:
            logging.error(f"Error in _get_cozy_spots: {str(e)}")
            return "I couldn't retrieve cozy spots at the moment. Please try again later."

    # Event Discovery Handlers
    async def _get_free_events(self, _, timeframe: str) -> str:
        try:
            time_clause = ""
            if timeframe.lower() == "today":
                time_clause = "DATE(e.EventDateTime) = DATE('now')"
            elif timeframe.lower() == "this week":
                time_clause = "DATE(e.EventDateTime) BETWEEN DATE('now') AND DATE('now', '+7 days')"
            else:
                time_clause = "1=1"  # No specific time filter

            async with self.db.execute(f'''
                SELECT e.EventName, e.EventDateTime, c.BuildingName,
                       e.EventDescription, e.OrganizerContact
                FROM EventInformation e
                JOIN CampusInformation c ON e.EventLocationID = c.BuildingID
                WHERE {time_clause}
                AND (
                    LOWER(e.EventDescription) LIKE '%free%'
                )
                ORDER BY e.EventDateTime
                LIMIT 5
            ''') as cursor:
                events = await cursor.fetchall()

            if not events:
                return f"No free events found {timeframe}. Try asking about different times!"

            response = f"🎟️ **Free events {timeframe}:**\n\n"
            for event in events:
                event_time = datetime.strptime(event[1], '%Y-%m-%d %H:%M:%S').strftime('%A, %B %d at %I:%M %p')
                response += (f"• **{event[0]}** at **{event[2]}**\n"
                             f"  🕒 When: {event_time}\n"
                             f"  {event[3]}\n"
                             f"  📞 Contact: {event[4]}\n")
            
            return response
        except Exception as e:
            logging.error(f"Error in _get_free_events: {str(e)}")
            return "I couldn't fetch free events at the moment. Please try again later."

    async def _get_club_meetings(self, _, timeframe: str) -> str:
        try:
            time_clause = ""
            if timeframe.lower() == "today":
                time_clause = "DATE(e.EventDateTime) = DATE('now')"
            elif timeframe.lower() == "this week":
                time_clause = "DATE(e.EventDateTime) BETWEEN DATE('now') AND DATE('now', '+7 days')"
            else:
                time_clause = "1=1"  # No specific time filter

            async with self.db.execute(f'''
                SELECT c.ClubName, e.EventDateTime, ci.BuildingName, e.EventDescription, e.OrganizerContact
                FROM ClubMeetings c
                JOIN EventInformation e ON c.MeetingID = e.EventID
                JOIN CampusInformation ci ON e.EventLocationID = ci.BuildingID
                WHERE {time_clause}
                ORDER BY e.EventDateTime
                LIMIT 5
            ''') as cursor:
                meetings = await cursor.fetchall()

            if not meetings:
                return f"No club meetings found {timeframe}. Try asking about different times!"

            response = f"🤝 **Club meetings {timeframe}:**\n\n"
            for meeting in meetings:
                event_time = datetime.strptime(meeting[1], '%Y-%m-%d %H:%M:%S').strftime('%A, %B %d at %I:%M %p')
                response += (f"• **{meeting[0]}** at **{meeting[2]}**\n"
                             f"  🕒 When: {event_time}\n"
                             f"  {meeting[3]}\n"
                             f"  📞 Contact: {meeting[4]}\n")
            
            return response
        except Exception as e:
            logging.error(f"Error in _get_club_meetings: {str(e)}")
            return "I couldn't fetch club meetings at the moment. Please try again later."

    async def _get_highlighted_events(self, _, qualifier: Optional[str], timeframe: str) -> str:
        try:
            time_clause = ""
            if timeframe.lower() == "today":
                time_clause = "DATE(e.EventDateTime) = DATE('now')"
            elif timeframe.lower() == "tonight":
                time_clause = "DATE(e.EventDateTime) = DATE('now') AND TIME(e.EventDateTime) >= '17:00'"
            elif timeframe.lower() == "this week":
                time_clause = "DATE(e.EventDateTime) BETWEEN DATE('now') AND DATE('now', '+7 days')"
            else:
                time_clause = "1=1"  # No specific time filter

            async with self.db.execute(f'''
                SELECT e.EventName, e.EventDateTime, c.BuildingName,
                       e.EventDescription, e.OrganizerContact
                FROM EventInformation e
                JOIN CampusInformation c ON e.EventLocationID = c.BuildingID
                WHERE {time_clause}
                AND (
                    LOWER(e.EventDescription) LIKE '%good%'
                    OR LOWER(e.EventDescription) LIKE '%interesting%'
                    OR LOWER(e.EventDescription) LIKE '%event%'
                )
                ORDER BY e.EventDateTime
                LIMIT 5
            ''') as cursor:
                events = await cursor.fetchall()

            if not events:
                return f"No highlighted events found {timeframe}. Try asking about different times!"

            response = f"🌟 **Highlighted events {timeframe}:**\n\n"
            for event in events:
                event_time = datetime.strptime(event[1], '%Y-%m-%d %H:%M:%S').strftime('%A, %B %d at %I:%M %p')
                response += (f"• **{event[0]}** at **{event[2]}**\n"
                             f"  🕒 When: {event_time}\n"
                             f"  {event[3]}\n"
                             f"  📞 Contact: {event[4]}\n")
            
            return response
        except Exception as e:
            logging.error(f"Error in _get_highlighted_events: {str(e)}")
            return "I couldn't fetch highlighted events at the moment. Please try again later."

    async def _get_personalized_suggestions(self, _, timeframe: str) -> str:
        try:
            # Placeholder for personalized suggestions logic
            # This could involve user preferences, history, etc.
            # For simplicity, we'll return a generic suggestion

            suggestions = {
                'today': "How about attending the guest lecture in the main hall or joining a study group at the library?",
                'tonight': "You might enjoy the open mic night at the student center or a movie screening at the campus cinema.",
                'this weekend': "Consider participating in the weekend hackathon or exploring the new art exhibition downtown."
            }

            suggestion = suggestions.get(timeframe.lower(), "Check out the latest events on the campus bulletin board!")

            response = f"💡 **Personalized Suggestions for {timeframe.capitalize()}:**\n\n• {suggestion}"
            return response
        except Exception as e:
            logging.error(f"Error in _get_personalized_suggestions: {str(e)}")
            return "I couldn't provide personalized suggestions at the moment. Please try again later."

    # Specific Time Queries Handlers
    async def _get_meal_recommendations(self, meal_type: str) -> str:
        try:
            current_time = datetime.now()
            
            meal_time_ranges = {
                'breakfast': ("06:00:00", "11:00:00"),
                'lunch': ("11:00:00", "15:00:00"),
                'dinner': ("15:00:00", "21:00:00")
            }

            time_start, time_end = meal_time_ranges.get(meal_type.lower(), ("06:00:00", "21:00:00"))

            async with self.db.execute('''
                SELECT BuildingName, Description, BuildingHours
                FROM CampusInformation 
                WHERE (LOWER(Description) LIKE '%breakfast%'
                OR LOWER(Description) LIKE '%lunch%'
                OR LOWER(Description) LIKE '%dinner%'
                OR LOWER(Description) LIKE '%food%'
                OR LOWER(Description) LIKE '%dining%')
                AND TIME(BuildingHours) BETWEEN ? AND ?
                ORDER BY BuildingName
                LIMIT 5
            ''', (time_start, time_end)) as cursor:
                meals = await cursor.fetchall()

            if not meals:
                return f"I couldn't find any {meal_type} places open right now. Try asking about different times!"

            response = f"🍽️ **{meal_type.capitalize()} Recommendations:**\n\n"
            for meal in meals:
                response += f"• **{meal[0]}**\n  {meal[1]}\n  🕒 Hours: {meal[2]}\n"

            return response
        except Exception as e:
            logging.error(f"Error in _get_meal_recommendations: {str(e)}")
            return "I couldn't retrieve meal recommendations at the moment. Please try again later."

    async def _get_coffee_by_time(self, hour: str, period: str) -> str:
        try:
            hour = int(hour)
            if period.lower() == "pm" and hour != 12:
                hour += 12
            elif period.lower() == "am" and hour == 12:
                hour = 0
            time_str = f"{hour:02}:00:00"

            async with self.db.execute('''
                SELECT BuildingName, Description, BuildingHours
                FROM CampusInformation 
                WHERE LOWER(Description) LIKE '%coffee%'
                AND TIME(BuildingHours) <= ?
                ORDER BY BuildingName
                LIMIT 5
            ''', (time_str,)) as cursor:
                coffees = await cursor.fetchall()

            if not coffees:
                return f"I couldn't find any coffee spots open at {hour % 12 or 12} {period.upper()}. Try asking about different times!"

            response = f"☕ **Coffee spots open at {hour % 12 or 12} {period.upper()}:**\n\n"
            for coffee in coffees:
                response += f"• **{coffee[0]}**\n  {coffee[1]}\n  🕒 Hours: {coffee[2]}\n"

            return response
        except Exception as e:
            logging.error(f"Error in _get_coffee_by_time: {str(e)}")
            return "I couldn't find coffee spots for the specified time. Please try again later."

    async def _get_events_by_time(self, _, hour: str, period: str) -> str:
        try:
            hour = int(hour)
            if period.lower() == "pm" and hour != 12:
                hour += 12
            elif period.lower() == "am" and hour == 12:
                hour = 0
            time_str = f"{hour:02}:00:00"

            async with self.db.execute('''
                SELECT e.EventName, e.EventDateTime, c.BuildingName,
                       e.EventDescription, e.OrganizerContact
                FROM EventInformation e
                JOIN CampusInformation c ON e.EventLocationID = c.BuildingID
                WHERE TIME(e.EventDateTime) = ?
                ORDER BY e.EventDateTime
                LIMIT 5
            ''', (time_str,)) as cursor:
                events = await cursor.fetchall()

            if not events:
                return f"No events found at {hour % 12 or 12} {period.upper()}. Try asking about different times!"

            response = f"📅 **Events happening at {hour % 12 or 12} {period.upper()}:**\n\n"
            for event in events:
                event_time = datetime.strptime(event[1], '%Y-%m-%d %H:%M:%S').strftime('%I:%M %p')
                response += (f"• **{event[0]}** at **{event[2]}**\n"
                             f"  🕒 When: {event_time}\n"
                             f"  {event[3]}\n"
                             f"  📞 Contact: {event[4]}\n")
            
            return response
        except Exception as e:
            logging.error(f"Error in _get_events_by_time: {str(e)}")
            return "I couldn't fetch events for the specified time. Please try again later."

    # Group Activity Handlers
    async def _get_group_study_spots(self) -> str:
        try:
            current_time = datetime.now()
            
            async with self.db.execute('''
                SELECT BuildingName, Description, BuildingHours
                FROM CampusInformation 
                WHERE LOWER(Description) LIKE '%group study%'
                OR LOWER(Description) LIKE '%collaborative%'
                ORDER BY BuildingName
                LIMIT 5
            ''', (f'%{current_time.strftime("%H:%M")}%',)) as cursor:
                spots = await cursor.fetchall()

            if not spots:
                return "I couldn't find any group study spots open right now. Try asking about specific times!"

            response = "👥 **Group study spots available now:**\n\n"
            for spot in spots:
                response += f"• **{spot[0]}**\n  {spot[1]}\n  🕒 Hours: {spot[2]}\n"

            return response
        except Exception as e:
            logging.error(f"Error in _get_group_study_spots: {str(e)}")
            return "I couldn't retrieve group study spots at the moment. Please try again later."

    async def _get_meeting_spaces(self, _, purpose: str) -> str:
        try:
            async with self.db.execute('''
                SELECT BuildingName, Description, BuildingHours
                FROM CampusInformation 
                WHERE LOWER(Description) LIKE '%meeting%'
                OR LOWER(Description) LIKE '%conference%'
                ORDER BY BuildingName
                LIMIT 5
            ''') as cursor:
                spaces = await cursor.fetchall()

            if not spaces:
                return f"I couldn't find any meeting spaces for {purpose}. Please try a different purpose!"

            response = f"📋 **Meeting spaces for {purpose}:**\n\n"
            for space in spaces:
                response += f"• **{space[0]}**\n  {space[1]}\n  🕒 Hours: {space[2]}\n"

            return response
        except Exception as e:
            logging.error(f"Error in _get_meeting_spaces: {str(e)}")
            return "I couldn't find meeting spaces at the moment. Please try again later."

    async def _get_meetup_spots(self) -> str:
        try:
            async with self.db.execute('''
                SELECT BuildingName, Description, BuildingHours
                FROM CampusInformation 
                WHERE LOWER(Description) LIKE '%meet friends%'
                OR LOWER(Description) LIKE '%socialize%'
                ORDER BY BuildingName
                LIMIT 5
            ''') as cursor:
                spots = await cursor.fetchall()

            if not spots:
                return "I couldn't find any places to meet friends right now. Try asking about different locations or times!"

            response = "👫 **Good places to meet friends:**\n\n"
            for spot in spots:
                response += f"• **{spot[0]}**\n  {spot[1]}\n  🕒 Hours: {spot[2]}\n"

            return response
        except Exception as e:
            logging.error(f"Error in _get_meetup_spots: {str(e)}")
            return "I couldn't find meetup spots at the moment. Please try again later."

    async def _get_fun_events(self) -> str:
        try:
            logging.info("Executing _get_fun_events")
            
            # First, let's check what events exist in the database
            debug_query = """
                SELECT DISTINCT
                    e.EventName,
                    e.EventDateTime,
                    c.BuildingName,
                    e.EventDescription
                FROM EventInformation e
                JOIN CampusInformation c ON e.EventLocationID = c.BuildingID
                ORDER BY e.EventDateTime
            """
            
            async with self.db.execute(debug_query) as cursor:
                all_events = await cursor.fetchall()
            logging.info(f"Total events in database: {len(all_events)}")
            if all_events:
                logging.info(f"Sample event: {all_events[0]}")
            
            # Now try the actual query without the date filter
            query = """
                SELECT DISTINCT
                    e.EventName,
                    e.EventDateTime,
                    c.BuildingName,
                    e.EventDescription
                FROM EventInformation e
                JOIN CampusInformation c ON e.EventLocationID = c.BuildingID
                ORDER BY e.EventDateTime
            """
            
            async with self.db.execute(query) as cursor:
                events = await cursor.fetchall()
            
            if not events:
                return "There are no events in the database. Check back later for new events!"
            
            response = "Here are the upcoming events:\n\n"
            
            seen_events = set()
            
            for event in events:
                event_name, event_time, location, description = event
                event_key = f"{event_name}_{event_time}_{location}"
                
                if event_key in seen_events:
                    continue
                    
                seen_events.add(event_key)
                
                formatted_time = datetime.strptime(event_time, '%Y-%m-%d %H:%M:%S').strftime('%B %d at %I:%M %p')
                
                response += f"Event: {event_name}\n"
                response += f"When: {formatted_time}\n"
                response += f"Where: {location}\n"
                if description:
                    response += f"Details: {description}\n"
                response += "\n"
            
            return response.strip()
            
        except Exception as e:
            logging.error(f"Error getting events: {str(e)}")
            logging.error(f"Exception type: {type(e)}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")
            return "Sorry, I had trouble finding the events. Please try asking again!"
        
    async def _get_student_organizations(self) -> str:
        try:
            logging.info("Executing _get_student_organizations")
            
            # Debug query to check what's in the database
            debug_query = """
                SELECT DISTINCT
                    o.OrgName,
                    o.OrgDescription,
                    o.MeetingSchedule,
                    c.BuildingName
                FROM StudentOrganizations o
                JOIN CampusInformation c ON o.MeetingLocationID = c.BuildingID
                WHERE o.IsActive = 1
                ORDER BY o.OrgName
            """
            
            async with self.db.execute(debug_query) as cursor:
                all_orgs = await cursor.fetchall()
            logging.info(f"Total organizations in database: {len(all_orgs)}")
            if all_orgs:
                logging.info(f"Sample organization: {all_orgs[0]}")
            
            # Main query
            query = """
                SELECT DISTINCT
                    o.OrgName,
                    o.OrgDescription,
                    o.MeetingSchedule,
                    c.BuildingName
                FROM StudentOrganizations o
                JOIN CampusInformation c ON o.MeetingLocationID = c.BuildingID
                WHERE o.IsActive = 1
                ORDER BY o.OrgName
            """
            
            async with self.db.execute(query) as cursor:
                organizations = await cursor.fetchall()
            
            if not organizations:
                return "There are no active student organizations in the database. Please check back later!"
            
            response = "** ACTIVE STUDENT ORGANIZATIONS **  \n\n"
            
            seen_orgs = set()
            
            for org in organizations:
                org_name, description, schedule, location = org
                org_key = f"{org_name}_{location}"
                
                if org_key in seen_orgs:
                    continue
                        
                seen_orgs.add(org_key)
                
                response += f"* **{org_name}**  \n"
                response += f"  Meeting Location: **{location}**  \n"
                if schedule:
                    response += f"  Schedule: {schedule}  \n"
                if description:
                    response += f"  About: {description}  \n"
                response += "\n"
            
            return response.strip()
            
        except Exception as e:
            logging.error(f"Error getting student organizations: {str(e)}")
            logging.error(f"Exception type: {type(e)}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")
            return "Sorry, I had trouble finding the student organizations. Please try asking again!"