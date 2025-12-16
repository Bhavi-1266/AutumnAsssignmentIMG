import  '../styles/loginPage.css';

type EntryBoxProps = {
  displayText: string;
  onClick?: () => void;
};

function EntryBox({ displayText, onClick }: EntryBoxProps) {
  return (
    <div
      onClick={onClick}
      role="button"
      tabIndex={0}
      className="
       entry-box
      "
    >
      {displayText}
    </div>
  );
}

export default EntryBox;
