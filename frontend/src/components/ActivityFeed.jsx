export default function ActivityFeed() {
  const activities = [
    "Task #5 moved to DONE",
    "Manager approved leave request",
    "New document uploaded",
  ];

  return (
    <div className="bg-white p-6 rounded-xl shadow-md">
      <h2 className="text-2xl font-semibold mb-4">
        Activity Feed
      </h2>

      <div className="space-y-3">
        {activities.map((activity, index) => (
          <div
            key={index}
            className="border-b pb-2"
          >
            {activity}
          </div>
        ))}
      </div>
    </div>
  );
}