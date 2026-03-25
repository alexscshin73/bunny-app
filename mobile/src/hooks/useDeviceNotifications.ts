import AsyncStorage from "@react-native-async-storage/async-storage";
import * as Notifications from "expo-notifications";
import { AppState, Platform } from "react-native";
import { useEffect, useMemo, useRef, useState } from "react";

const NOTIFICATION_PREFERENCE_STORAGE_KEY = "bunny.notifications_enabled";
const ANDROID_CHANNEL_ID = "conversation-updates";

type NotificationPermissionState = "undetermined" | "denied" | "granted";

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldPlaySound: true,
    shouldSetBadge: true,
    shouldShowBanner: true,
    shouldShowList: true,
  }),
});

function permissionStateFromSettings(
  settings: Notifications.NotificationPermissionsStatus
): NotificationPermissionState {
  if (settings.status === "granted") {
    return "granted";
  }
  if (settings.status === "denied") {
    return "denied";
  }
  return "undetermined";
}

async function ensureAndroidChannel() {
  if (Platform.OS !== "android") {
    return;
  }

  await Notifications.setNotificationChannelAsync(ANDROID_CHANNEL_ID, {
    name: "Conversation updates",
    importance: Notifications.AndroidImportance.HIGH,
    lightColor: "#d97745",
    vibrationPattern: [0, 250, 250, 250],
  });
}

interface NotifyOptions {
  body: string;
  data?: Record<string, string>;
  title: string;
}

export function useDeviceNotifications() {
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [permissionStatus, setPermissionStatus] =
    useState<NotificationPermissionState>("undetermined");
  const [isUpdatingNotifications, setIsUpdatingNotifications] = useState(false);
  const appStateRef = useRef(AppState.currentState);
  const badgeCountRef = useRef(0);

  useEffect(() => {
    AsyncStorage.getItem(NOTIFICATION_PREFERENCE_STORAGE_KEY)
      .then((storedValue) => {
        if (storedValue === "false") {
          setNotificationsEnabled(false);
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    ensureAndroidChannel()
      .then(() => Notifications.getPermissionsAsync())
      .then((settings) => {
        setPermissionStatus(permissionStateFromSettings(settings));
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    const subscription = AppState.addEventListener("change", (nextState) => {
      appStateRef.current = nextState;
      if (nextState === "active") {
        badgeCountRef.current = 0;
        Notifications.setBadgeCountAsync(0).catch(() => {});
      }
    });

    return () => {
      subscription.remove();
    };
  }, []);

  async function updateNotificationsEnabled(nextEnabled: boolean) {
    setIsUpdatingNotifications(true);
    try {
      setNotificationsEnabled(nextEnabled);
      await AsyncStorage.setItem(
        NOTIFICATION_PREFERENCE_STORAGE_KEY,
        nextEnabled ? "true" : "false"
      );

      if (!nextEnabled) {
        badgeCountRef.current = 0;
        await Notifications.setBadgeCountAsync(0).catch(() => false);
        return;
      }

      await ensureAndroidChannel();
      let settings = await Notifications.getPermissionsAsync();
      if (settings.status !== "granted") {
        settings = await Notifications.requestPermissionsAsync();
      }
      setPermissionStatus(permissionStateFromSettings(settings));
    } finally {
      setIsUpdatingNotifications(false);
    }
  }

  async function notifyConversationUpdate({ body, data, title }: NotifyOptions) {
    if (!notificationsEnabled || permissionStatus !== "granted") {
      return false;
    }
    if (appStateRef.current === "active") {
      return false;
    }

    badgeCountRef.current += 1;
    await Notifications.setBadgeCountAsync(badgeCountRef.current).catch(() => false);
    await ensureAndroidChannel();
    await Notifications.scheduleNotificationAsync({
      content: {
        body,
        data,
        title,
      },
      trigger: null,
    });
    return true;
  }

  const notificationStatusText = useMemo(() => {
    if (!notificationsEnabled) {
      return "Notifications are turned off on this device.";
    }
    if (permissionStatus === "granted") {
      return Platform.OS === "android"
        ? "Android notifications are ready on this device."
        : "iOS notifications are ready on this device.";
    }
    if (permissionStatus === "denied") {
      return "Notifications are enabled here, but OS permission is denied.";
    }
    return Platform.OS === "android"
      ? "Android 13+ will ask for notification permission when you enable alerts."
      : "iOS will ask for notification permission when you enable alerts.";
  }, [notificationsEnabled, permissionStatus]);

  const platformStatusText = useMemo(() => {
    if (Platform.OS === "android") {
      return "Android emulator should use 10.0.2.2 for a local Mac backend. Local alerts work here, but real remote push still needs a device build.";
    }
    if (Platform.OS === "ios") {
      return "iOS simulator on the same Mac can use 127.0.0.1. Local alerts work here, but real remote push still needs a physical iPhone.";
    }
    return "Web keeps browser-specific behavior, while the native app uses on-device alert permissions.";
  }, []);

  return {
    isUpdatingNotifications,
    notificationStatusText,
    notificationsEnabled,
    permissionStatus,
    platformStatusText,
    notifyConversationUpdate,
    setNotificationsEnabled: updateNotificationsEnabled,
  };
}
