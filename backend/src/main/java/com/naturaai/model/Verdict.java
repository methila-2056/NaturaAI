package com.naturaai.model;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

import java.util.Locale;

public enum Verdict {
    SAFE,
    CAUTION,
    UNSAFE;

    @JsonValue
    public String jsonValue() {
        return name().toLowerCase(Locale.ROOT);
    }

    @JsonCreator
    public static Verdict fromValue(String value) {
        if (value == null) {
            return null;
        }
        for (Verdict verdict : values()) {
            if (verdict.name().equalsIgnoreCase(value) || verdict.jsonValue().equalsIgnoreCase(value)) {
                return verdict;
            }
        }
        throw new IllegalArgumentException("Unknown verdict: " + value);
    }
}
