// Last time updated on June 08, 2018

// Latest file can be found here: https://cdn.webrtc-experiment.com/getScreenId.js

// Muaz Khan         - www.MuazKhan.com
// MIT License       - www.WebRTC-Experiment.com/licence
// Documentation     - https://github.com/muaz-khan/getScreenId.

// ______________
// getScreenId.js

/*
getScreenId(function (error, sourceId, screen_constraints) {
    // error    == null || 'permission-denied' || 'not-installed' || 'installed-disabled' || 'not-chrome'
    // sourceId == null || 'string' || 'firefox'
    
    if(microsoftEdge) {
        navigator.getDisplayMedia(screen_constraints).then(onSuccess, onFailure);
    }
    else {
        navigator.mediaDevices.getUserMedia(screen_constraints).then(onSuccess)catch(onFailure);
    }

}, 'pass second parameter only if you want system audio');
*/

(function() {
    window.getScreenId = function(callback, custom_parameter) {
        if(navigator.userAgent.indexOf('Edge') !== -1 && (!!navigator.msSaveOrOpenBlob || !!navigator.msSaveBlob)) {
            // microsoft edge => navigator.getDisplayMedia(screen_constraints).then(onSuccess, onFailure);
            callback({
                video: true
            });
            return;
        }

        // for Firefox:
        // sourceId == 'firefox'
        // screen_constraints = {...}
        if (!!navigator.mozGetUserMedia) {
            callback(null, 'firefox', {
                video: {
                    mozMediaSource: 'window',
                    mediaSource: 'window'
                }
            });
            return;
        }
    };

    function getScreenConstraints(error, sourceId, canRequestAudioTrack) {
        var screen_constraints = {
            audio: false,
            video: {
                mandatory: {
                    chromeMediaSource: error ? 'screen' : 'desktop',
                    // maxWidth: window.screen.width > 1920 ? window.screen.width : 1920,
                    // maxHeight: window.screen.height > 1080 ? window.screen.height : 1080
                },
                optional: []
            }
        };

        if(!!canRequestAudioTrack) {
            screen_constraints.audio = {
                mandatory: {
                    chromeMediaSource: error ? 'screen' : 'desktop',
                    // echoCancellation: true
                },
                optional: []
            };
        }

        if (sourceId) {
            screen_constraints.video.mandatory.chromeMediaSourceId = sourceId;

            if(screen_constraints.audio && screen_constraints.audio.mandatory) {
                screen_constraints.audio.mandatory.chromeMediaSourceId = sourceId;
            }
        }

        return screen_constraints;
    }

    
})();