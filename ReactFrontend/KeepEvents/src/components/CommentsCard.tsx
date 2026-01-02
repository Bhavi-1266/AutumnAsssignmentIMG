import { useState } from "react";
import { deleteComment } from "../services/Photos.ts"; // Your delete service
import { toast } from "react-hot-toast";

interface CommentsCardProps {
  comment: {
    id: number;
    commentText: string;
    commentedAt: string;
    photo: {
      photoid: number;
      photoFile: string;
      title?: string;
    };
  };
  onDelete: (commentId: number) => void;
}

function CommentsCard({ comment, onDelete }: CommentsCardProps) {
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async () => {
    if (deleting) return;
    
    setDeleting(true);
    try {
      await deleteComment(comment.id);
      onDelete(comment.id);
      toast.success("Comment deleted");
    } catch (err) {
      toast.error("Failed to delete comment");
      console.error(err);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="group bg-white p-4 rounded-xl shadow-sm border border-gray-200 hover:shadow-md hover:border-gray-300 transition-all duration-200 cursor-pointer">
      <div className="flex items-start gap-3">
        {/* Small Photo */}
        <div className="flex-shrink-0 w-16 h-16 rounded-lg overflow-hidden shadow-sm ring-1 ring-gray-200">
          <img
            src={comment.photo.photoFile}
            alt={comment.photo.title || `Photo ${comment.photo.photoid}`}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
            draggable={false}
          />
        </div>

        {/* Text Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <p className="font-medium text-sm text-gray-900 truncate">
              {comment.photo.title || `Photo ${comment.photo.photoid}`}
            </p>
            <button
              onClick={handleDelete}
              disabled={deleting}
              className="ml-2 p-1 rounded-full hover:bg-red-50 hover:text-red-600 transition-colors text-gray-400 hover:text-red-500 disabled:opacity-50"
              title="Delete comment"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
          
          <p className="text-sm text-gray-600 line-clamp-2 mb-2 leading-relaxed">
            "{comment.commentText}"
          </p>
          
          <p className="text-xs text-gray-400">
            {new Date(comment.commentedAt).toLocaleDateString()}
          </p>
        </div>
      </div>
    </div>
  );
}

export default CommentsCard;
