import type { Photo } from "../types/photos";

interface PhotoCardProps {
  photo: Photo;
  onClick?: () => void;
}

function PhotoCard({ photo, onClick }: PhotoCardProps) {    

  return (
    <div
      onClick={onClick}
      className="flex flex-col rouded-lg .h-full  border border-gray-300 shadow-md hover:shadow-lg cursor-pointer transition-shadow duration-200"
    >
      {/* Cover Image */}
      <div className="">
        {photo.photoFile ? (
          <img
            src={photo.photoFile}
            alt={photo.photoDesc || "Photo"}
            className=" h-48 w-full object-contain"
          />
        ) : (
          <div className="  h-48 w-full flex items-center justify-center text-gray-500">
            No Image
          </div>
        )}
      </div>
    </div>
     
  );
}

export default PhotoCard    ;
