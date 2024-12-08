import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import ChatPage from './ChatPage';

// Mock scrollIntoView
window.HTMLElement.prototype.scrollIntoView = jest.fn();

// Mock AuthContext values
jest.mock('../context/AuthContext', () => ({
    useAuth: () => ({
        user: { id: 1, username: 'testuser', role: 'user' }
    }),
    AuthProvider: ({ children }) => <div>{children}</div>
}));

// Helper function to render ChatPage with required providers
const renderChatPage = () => {
    return render(
        <BrowserRouter>
            <AuthProvider>
                <ChatPage />
            </AuthProvider>
        </BrowserRouter>
    );
};

describe('ChatPage Component', () => {
    const originalError = console.error;

    beforeAll(() => {
        // Suppress console.error for expected warnings
        console.error = (...args) => {
            if (
                !args[0].includes('Error fetching sessions') &&
                !args[0].includes('Warning: Encountered two children with the same key')
            ) {
                originalError(...args);
            }
        };
    });

    afterAll(() => {
        // Restore original console.error
        console.error = originalError;
    });

    beforeEach(() => {
        // Clear all mocks and prepare default fetch
        jest.clearAllMocks();
        window.HTMLElement.prototype.scrollIntoView.mockClear();

        global.fetch = jest.fn(() =>
            Promise.resolve({
                ok: true,
                json: () => Promise.resolve({
                    sessions: [],
                    messages: []
                })
            })
        );
    });

    afterEach(() => {
        // Clean up after each test
        jest.clearAllTimers();
    });

    describe('Initial Rendering', () => {
        test('renders welcome screen initially', async () => {
            renderChatPage();
            await waitFor(() => {
                expect(screen.getByText(/How can I help you today?/i)).toBeInTheDocument();
            });
        });

        test('renders category buttons on initial load', async () => {
            renderChatPage();
            await waitFor(() => {
                expect(screen.getByText(/Quick Info/i)).toBeInTheDocument();
                expect(screen.getByText(/Study & Workspace/i)).toBeInTheDocument();
                expect(screen.getByText(/Food & Drinks/i)).toBeInTheDocument();
            });
        });

        test('renders new chat button in sidebar', async () => {
            renderChatPage();
            await waitFor(() => {
                expect(screen.getByText(/New chat/i)).toBeInTheDocument();
            });
        });

        test('renders empty chat history initially', async () => {
            const { container } = renderChatPage();

            await waitFor(() => {
                const sidebar = container.querySelector('.sidebar');
                expect(sidebar).toBeInTheDocument();
                const chatHistoryList = container.querySelector('.chat-history-list');
                expect(chatHistoryList).toBeInTheDocument();
                expect(chatHistoryList.children.length).toBe(0);
            });
        });
    });

    describe('Message Handling', () => {
        test('displays user message in chat history when sent', async () => {
            const mockSessionResponse = { sessionId: 1 };
            const testMessage = "What's happening right now?";

            // Mock fetch responses
            global.fetch
                .mockImplementationOnce(() => Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve({ sessions: [] })
                }))
                .mockImplementationOnce(() => Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve(mockSessionResponse)
                }))
                .mockImplementationOnce(() => Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve({ response: "Here's what's happening on campus..." })
                }));

            renderChatPage();

            // User sends a message
            await waitFor(() => {
                const categoryButton = screen.getByText('Quick Info');
                fireEvent.click(categoryButton);
            });

            await waitFor(() => {
                const questionButton = screen.getByText(testMessage);
                fireEvent.click(questionButton);
            });

            // Verify the user message appears in the chat
            await waitFor(() => {
                expect(screen.getByText(testMessage)).toBeInTheDocument();
            });
        });
    });

    describe('Category Selection', () => {
        test('displays relevant questions when category is selected', async () => {
            renderChatPage();

            await waitFor(() => {
                const categoryButton = screen.getByText(/Study & Workspace/i);
                fireEvent.click(categoryButton);
            });

            await waitFor(() => {
                expect(screen.getByText(/What buildings are open/i)).toBeInTheDocument();
                expect(screen.getByText(/Where can I study with a group/i)).toBeInTheDocument();
            });
        });

        test('allows returning to categories view', async () => {
            renderChatPage();

            await waitFor(() => {
                const categoryButton = screen.getByText(/Study & Workspace/i);
                fireEvent.click(categoryButton);
            });

            const backButton = screen.getByText(/Back to Categories/i);
            fireEvent.click(backButton);

            await waitFor(() => {
                expect(screen.getByText(/Quick Info/i)).toBeInTheDocument();
                expect(screen.getByText(/Food & Drinks/i)).toBeInTheDocument();
            });
        });
    });

    describe('Session Management', () => {
        test('fetches and displays sessions successfully', async () => {
            const mockSessions = {
                sessions: [
                    {
                        SessionID: 1,
                        SessionStartTime: '2024-12-08T10:00:00',
                        FirstMessage: 'Test message'
                    }
                ]
            };

            global.fetch.mockImplementationOnce(() =>
                Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve(mockSessions)
                })
            );

            renderChatPage();

            await waitFor(() => {
                expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/sessions'));
            });
        });

        test('creates new session when New Chat button is clicked', async () => {
            const mockSessionResponse = { sessionId: 1 };

            global.fetch
                .mockImplementationOnce(() => Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve({ sessions: [] })
                }))
                .mockImplementationOnce(() => Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve(mockSessionResponse)
                }));

            renderChatPage();

            await waitFor(() => {
                const newChatButton = screen.getByText(/New chat/i);
                fireEvent.click(newChatButton);
            });

            await waitFor(() => {
                expect(fetch).toHaveBeenNthCalledWith(2,
                    expect.stringContaining('/sessions'),
                    expect.objectContaining({
                        method: 'POST',
                        headers: expect.any(Object)
                    })
                );
            });
        });

        test('deletes chat session when delete button is clicked', async () => {
            const mockSessions = {
                sessions: [
                    {
                        SessionID: 1,
                        SessionStartTime: '2024-12-08T10:00:00',
                        FirstMessage: 'Test message'
                    }
                ]
            };

            global.fetch
                .mockImplementationOnce(() => Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve(mockSessions)
                }))
                .mockImplementationOnce(() => Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve({ status: 'success' })
                }))
                .mockImplementationOnce(() => Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve({ sessions: [] })
                }));

            const { container } = renderChatPage();

            await waitFor(() => {
                const deleteButton = container.querySelector('.delete-session-button');
                expect(deleteButton).toBeInTheDocument();
                fireEvent.click(deleteButton);
            });

            await waitFor(() => {
                expect(fetch).toHaveBeenCalledWith(
                    expect.stringContaining('/sessions/1'),
                    expect.objectContaining({ method: 'DELETE' })
                );
            });

            await waitFor(() => {
                const chatHistoryList = container.querySelector('.chat-history-list');
                expect(chatHistoryList.children.length).toBe(0);
            });
        });
    });

    describe('Error Handling', () => {
        test('displays error message when fetch fails', async () => {
            global.fetch.mockImplementationOnce(() =>
                Promise.reject(new Error('Failed to fetch'))
            );

            renderChatPage();

            await waitFor(() => {
                expect(screen.getByText(/Failed to load chat history/i)).toBeInTheDocument();
            });
        });
    });
});