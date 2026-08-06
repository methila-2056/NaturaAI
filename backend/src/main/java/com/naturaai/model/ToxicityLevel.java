package com.naturaai.model;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

import java.util.Locale;

public enum ToxicityLevel {
    LOW,
    MEDIUM,
    HIGH;

    @JsonValue
    public String jsonValue() {
        return name().toLowerCase(Locale.ROOT);
    }

    @JsonCreator
    public static ToxicityLevel fromValue(String value) {
        if (value == null) {
            return null;
        }
        for (ToxicityLevel level : values()) {
            if (level.name().equalsIgnoreCase(value) || level.jsonValue().equalsIgnoreCase(value)) {
                return level;
            }
        }
        throw new IllegalArgumentException("Unknown toxicity level: " + value);
    }
}
