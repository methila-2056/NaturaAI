import { beforeEach, describe, expect, it } from "vitest";
import { useUserStore, type UserProfile } from "./useUserStore";

const profile: UserProfile = {
  id: "1",
  fullName: "Jane Doe",
  email: "jane@example.com",
  age: 25,
  gender: "female",
  diseases: ["Diabetes"],
  allergies: [],
  medications: [],
};

describe("useUserStore", () => {
  beforeEach(() => {
    useUserStore.setState({ user: null, token: null });
    localStorage.clear();
  });

  it("starts logged out", () => {
    expect(useUserStore.getState().user).toBeNull();
    expect(useUserStore.getState().token).toBeNull();
  });

  it("setAuth stores user and token", () => {
    useUserStore.getState().setAuth(profile, "jwt-token");

    expect(useUserStore.getState().user).toEqual(profile);
    expect(useUserStore.getState().token).toBe("jwt-token");
  });

  it("updateProfile merges only provided fields", () => {
    useUserStore.getState().setAuth(profile, "jwt-token");
    useUserStore.getState().updateProfile({ age: 26, country: "IN" });

    const user = useUserStore.getState().user;
    expect(user?.age).toBe(26);
    expect(user?.country).toBe("IN");
    expect(user?.fullName).toBe("Jane Doe");
  });

  it("updateProfile is a no-op when logged out", () => {
    useUserStore.getState().updateProfile({ age: 30 });
    expect(useUserStore.getState().user).toBeNull();
  });

  it("logout clears user and token", () => {
    useUserStore.getState().setAuth(profile, "jwt-token");
    useUserStore.getState().logout();

    expect(useUserStore.getState().user).toBeNull();
    expect(useUserStore.getState().token).toBeNull();
  });

  it("persists to localStorage under naturaai-store", () => {
    useUserStore.getState().setAuth(profile, "jwt-token");

    const raw = localStorage.getItem("naturaai-store");
    expect(raw).not.toBeNull();
    expect(JSON.parse(raw as string).state.user.email).toBe("jane@example.com");
  });
});
