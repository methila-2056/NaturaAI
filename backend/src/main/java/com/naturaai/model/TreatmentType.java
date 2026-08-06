package com.naturaai.model;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

import java.util.Locale;

public enum TreatmentType {
    INTERNAL,
    EXTERNAL;

    @JsonValue
    public String jsonValue() {
        return name().toLowerCase(Locale.ROOT);
    }

    @JsonCreator
    public static TreatmentType fromValue(String value) {
        if (value == null) {
            return null;
        }
        for (TreatmentType type : values()) {
            if (type.name().equalsIgnoreCase(value) || type.jsonValue().equalsIgnoreCase(value)) {
                return type;
            }
        }
        throw new IllegalArgumentException("Unknown treatment type: " + value);
    }
}
