import React, {FC} from 'react';


export const Spinner: FC = () => {
  return (
    <div className="clickbait-checker-spinner-root">
      <div className="clickbait-checker-spinner ytp-spinner">
        <div>
          <div className="ytp-spinner-container">
            <div className="ytp-spinner-rotator">
              <div className="ytp-spinner-left">
                <div className="ytp-spinner-circle"></div>
              </div>
              <div className="ytp-spinner-right">
                <div className="ytp-spinner-circle"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
