interface SelectionBarProps {
  count: number;
  onClear: () => void;
  onDelete: () => void;
}

function SelectionBar({ count, onClear, onDelete }: SelectionBarProps) {
  return (
    <div className="fixed top-16 left-0 right-0 z-40 bg-gray-900 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-6 py-3 flex justify-between items-center">
        <span className="font-medium">
          {count} selected  
        </span>

        <div className="flex gap-3">
          <button
            onClick={onDelete}
            className="px-4 py-1.5 bg-red-600 hover:bg-red-700 rounded"
          >
            Delete
          </button>

          <button
            onClick={onClear}
            className="px-4 py-1.5 bg-gray-700 hover:bg-gray-600 rounded"
          >
            Clear
          </button>
        </div>
      </div>
    </div>
  );
}

export default SelectionBar;
