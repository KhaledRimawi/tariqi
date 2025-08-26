
import { LogLevel } from '@azure/msal-browser';

export const msalConfig = {
    auth: {
        clientId: process.env.REACT_APP_CLIENT_ID, 
        authority:  process.env.REACT_APP_AUTHORITY, 
        redirectUri: process.env.REACT_APP_REDIRECT_URI, 
        postLogoutRedirectUri: process.env.REACT_APP_REDIRECT_URI, 
        navigateToLoginRequestUrl: false, 
    },
    cache: {
        cacheLocation: 'sessionStorage', 
        storeAuthStateInCookie: false, 
    },
    system: {
        loggerOptions: {
            loggerCallback: (level, message, containsPii) => {
                if (containsPii) {
                    return;
                }
                switch (level) {
                    case LogLevel.Error:
                        console.error(message);
                        return;
                    case LogLevel.Info:
                        console.info(message);
                        return;
                    case LogLevel.Verbose:
                        console.debug(message);
                        return;
                    case LogLevel.Warning:
                        console.warn(message);
                        return;
                    default:
                        return;
                }
            },
        },
    },
};

export const loginRequest = {
    scopes: ["User.Read"],
};

