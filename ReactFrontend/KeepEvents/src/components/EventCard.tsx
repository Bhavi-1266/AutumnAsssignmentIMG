import type { Event } from "../types/event";

interface EventCardProps {
  event: Event;
  totalPhotos: number;
  onClick?: () => void;
}

function EventCard({ event, totalPhotos, onClick }: EventCardProps) {


  return (
    <div
      onClick={onClick}
      className="flex flex-col rouded-lg .h-full  border border-gray-300 shadow-md hover:shadow-lg cursor-pointer transition-shadow duration-200"
    >
      {/* Cover Image */}
      <div className="">
        {event.eventCoverPhoto_url ? (
          <img
            src={event.eventCoverPhoto_url}
            alt={event.eventname}
            className=" h-48 w-full object-contain"
          />
        ) : (
          <div className="  h-48 w-full flex items-center justify-center text-gray-500">
            No Image
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4">
        <h2 className="text-lg font-semibold mb-1">
          {event.eventname}
        </h2>

        <p className="text-sm text-gray-500 mb-2">
          {event.eventdate} · {event.eventtime}
        </p>

        <p className="text-sm text-gray-700 line-clamp-2 mb-3">
          {event.eventdesc}
        </p>

        <div className="flex justify-between items-center text-sm text-gray-600">
          <span>{event.eventlocation}</span>
          <span>{totalPhotos} photos</span>
        </div>
      </div>
    </div>
  );
}

export default EventCard;
