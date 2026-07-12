import { logger } from "../logger.js";

export interface CalendarEvent {
  id: string;
  summary: string;
  start: string;
  end: string;
  location?: string;
  attendees?: string[];
}

interface GoogleAuth {
  clientId: string;
  clientSecret: string;
  refreshToken: string;
  calendarId: string;
}

/**
 * Minimal Google Calendar client using the REST API with an OAuth refresh
 * token — no SDK dependency. Optional: only active when GOOGLE_* env vars
 * are configured.
 */
export class GoogleCalendar {
  private accessToken: string | null = null;
  private tokenExpiresAt = 0;

  constructor(private auth: GoogleAuth) {}

  private async getAccessToken(): Promise<string> {
    if (this.accessToken && Date.now() < this.tokenExpiresAt - 60_000) {
      return this.accessToken;
    }
    const res = await fetch("https://oauth2.googleapis.com/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        client_id: this.auth.clientId,
        client_secret: this.auth.clientSecret,
        refresh_token: this.auth.refreshToken,
        grant_type: "refresh_token",
      }),
    });
    if (!res.ok) {
      throw new Error(`Google token refresh failed: ${res.status} ${await res.text()}`);
    }
    const data = (await res.json()) as { access_token: string; expires_in: number };
    this.accessToken = data.access_token;
    this.tokenExpiresAt = Date.now() + data.expires_in * 1000;
    return this.accessToken;
  }

  async listEvents(timeMinISO: string, timeMaxISO: string): Promise<CalendarEvent[]> {
    const token = await this.getAccessToken();
    const url = new URL(
      `https://www.googleapis.com/calendar/v3/calendars/${encodeURIComponent(this.auth.calendarId)}/events`
    );
    url.searchParams.set("timeMin", timeMinISO);
    url.searchParams.set("timeMax", timeMaxISO);
    url.searchParams.set("singleEvents", "true");
    url.searchParams.set("orderBy", "startTime");
    url.searchParams.set("maxResults", "25");

    const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
    if (!res.ok) {
      throw new Error(`Calendar list failed: ${res.status} ${await res.text()}`);
    }
    const data = (await res.json()) as {
      items?: Array<{
        id: string;
        summary?: string;
        location?: string;
        start?: { dateTime?: string; date?: string };
        end?: { dateTime?: string; date?: string };
        attendees?: Array<{ email?: string }>;
      }>;
    };
    return (data.items ?? []).map((e) => ({
      id: e.id,
      summary: e.summary ?? "(no title)",
      start: e.start?.dateTime ?? e.start?.date ?? "",
      end: e.end?.dateTime ?? e.end?.date ?? "",
      location: e.location,
      attendees: e.attendees?.map((a) => a.email ?? "").filter(Boolean),
    }));
  }

  async createEvent(
    summary: string,
    startISO: string,
    endISO: string,
    description?: string,
    attendees?: string[]
  ): Promise<CalendarEvent> {
    const token = await this.getAccessToken();
    const res = await fetch(
      `https://www.googleapis.com/calendar/v3/calendars/${encodeURIComponent(this.auth.calendarId)}/events`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          summary,
          description,
          start: { dateTime: startISO },
          end: { dateTime: endISO },
          attendees: attendees?.map((email) => ({ email })),
        }),
      }
    );
    if (!res.ok) {
      throw new Error(`Calendar create failed: ${res.status} ${await res.text()}`);
    }
    const e = (await res.json()) as {
      id: string;
      summary?: string;
      start?: { dateTime?: string };
      end?: { dateTime?: string };
    };
    logger.info({ eventId: e.id }, "calendar event created");
    return {
      id: e.id,
      summary: e.summary ?? summary,
      start: e.start?.dateTime ?? startISO,
      end: e.end?.dateTime ?? endISO,
    };
  }
}
