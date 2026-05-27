"use client";
import useSWR from "swr";
import { calendarApi } from "@/lib/api";
import { useState } from "react";
import { format, startOfMonth, endOfMonth, eachDayOfInterval, getDay, addMonths, subMonths } from "date-fns";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { CONTENT_TYPE_COLORS } from "@/lib/utils";

export default function CalendarPage() {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const start = format(startOfMonth(currentMonth), "yyyy-MM-dd");
  const end = format(endOfMonth(currentMonth), "yyyy-MM-dd");

  const { data: entries = [] } = useSWR(
    ["calendar", start, end],
    () => calendarApi.list(start, end).then((r) => r.data),
    { revalidateOnFocus: false }
  );

  const days = eachDayOfInterval({ start: startOfMonth(currentMonth), end: endOfMonth(currentMonth) });
  const startPadding = getDay(startOfMonth(currentMonth)); // 0=Sun, 6=Sat

  const entriesByDate = entries.reduce((acc: Record<string, any[]>, entry: any) => {
    const d = entry.scheduled_date;
    if (!acc[d]) acc[d] = [];
    acc[d].push(entry);
    return acc;
  }, {});

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Content Calendar</h1>
        <div className="flex items-center gap-3">
          <button onClick={() => setCurrentMonth(subMonths(currentMonth, 1))} className="p-2 hover:bg-gray-100 rounded-lg">
            <ChevronLeft size={18} />
          </button>
          <span className="font-semibold text-gray-800 w-36 text-center">
            {format(currentMonth, "MMMM yyyy")}
          </span>
          <button onClick={() => setCurrentMonth(addMonths(currentMonth, 1))} className="p-2 hover:bg-gray-100 rounded-lg">
            <ChevronRight size={18} />
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
        {/* Day headers */}
        <div className="grid grid-cols-7 border-b border-gray-100">
          {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((d) => (
            <div key={d} className="py-3 text-center text-xs font-medium text-gray-400">{d}</div>
          ))}
        </div>

        {/* Calendar grid */}
        <div className="grid grid-cols-7">
          {/* Empty cells for padding */}
          {Array.from({ length: startPadding }).map((_, i) => (
            <div key={`pad-${i}`} className="min-h-[100px] border-b border-r border-gray-50 bg-gray-50/50" />
          ))}
          {/* Day cells */}
          {days.map((day) => {
            const dateStr = format(day, "yyyy-MM-dd");
            const dayEntries = entriesByDate[dateStr] || [];
            const isToday = dateStr === format(new Date(), "yyyy-MM-dd");
            return (
              <div key={dateStr} className={`min-h-[100px] p-2 border-b border-r border-gray-50 ${isToday ? "bg-indigo-50/40" : ""}`}>
                <div className={`text-sm font-medium mb-1 ${isToday ? "text-indigo-600" : "text-gray-500"}`}>
                  {format(day, "d")}
                </div>
                {dayEntries.slice(0, 3).map((entry: any) => (
                  <div
                    key={entry.id}
                    className="text-xs px-1.5 py-0.5 rounded mb-0.5 truncate bg-indigo-100 text-indigo-700"
                    title={entry.notes || entry.platform || "Scheduled"}
                  >
                    {entry.platform || "Content"}
                  </div>
                ))}
                {dayEntries.length > 3 && (
                  <div className="text-xs text-gray-400">+{dayEntries.length - 3} more</div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      <div className="mt-4 flex items-center gap-4 text-xs text-gray-500">
        <span>{entries.length} items scheduled this month</span>
        <span>Go to Content → set a scheduled date to add items to the calendar</span>
      </div>
    </div>
  );
}
