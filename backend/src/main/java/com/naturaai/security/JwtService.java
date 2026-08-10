package com.naturaai.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.Map;
import java.util.function.Function;

@Service
public class JwtService {

    private static final Logger logger = LoggerFactory.getLogger(JwtService.class);

    private static final long EMAIL_VERIFICATION_EXPIRATION_MS = 3_600_000L;

    private static final long PASSWORD_RESET_EXPIRATION_MS = 1_800_000L;

    private final SecretKey key;
    private final long expirationMs;

    public JwtService(
            @Value("${naturaai.jwt.secret}") String secret,
            @Value("${naturaai.jwt.expiration-ms}") long expirationMs) {
        this.key = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
        this.expirationMs = expirationMs;
    }

    public String generateToken(UserPrincipal principal) {
        return Jwts.builder()
                .subject(principal.getUsername())
                .claims(Map.of("role", principal.getRole()))
                .issuedAt(new Date())
                .expiration(new Date(System.currentTimeMillis() + expirationMs))
                .signWith(key)
                .compact();
    }

    public String generateEmailVerificationToken(String email) {
        return Jwts.builder()
                .subject(email)
                .claim("purpose", "email_verification")
                .issuedAt(new Date())
                .expiration(new Date(System.currentTimeMillis() + EMAIL_VERIFICATION_EXPIRATION_MS))
                .signWith(key)
                .compact();
    }

    public boolean isEmailVerificationToken(String token) {
        try {
            Claims claims = Jwts.parser()
                    .verifyWith(key)
                    .build()
                    .parseSignedClaims(token)
                    .getPayload();
            return "email_verification".equals(claims.get("purpose", String.class))
                    && !claims.getExpiration().before(new Date());
        } catch (Exception ex) {
            logger.warn("Verification token rejected: {}", ex.toString());
            return false;
        }
    }

    public String generatePasswordResetToken(String email) {
        return Jwts.builder()
                .subject(email)
                .claim("purpose", "password_reset")
                .issuedAt(new Date())
                .expiration(new Date(System.currentTimeMillis() + PASSWORD_RESET_EXPIRATION_MS))
                .signWith(key)
                .compact();
    }

    public boolean isPasswordResetToken(String token) {
        try {
            Claims claims = Jwts.parser()
                    .verifyWith(key)
                    .build()
                    .parseSignedClaims(token)
                    .getPayload();
            return "password_reset".equals(claims.get("purpose", String.class))
                    && !claims.getExpiration().before(new Date());
        } catch (Exception ex) {
            logger.warn("Password reset token rejected: {}", ex.toString());
            return false;
        }
    }

    public String extractUsername(String token) {
        return extractClaim(token, Claims::getSubject);
    }

    public boolean isTokenValid(String token, UserPrincipal principal) {
        try {
            final String username = extractUsername(token);
            return username.equals(principal.getUsername()) && !isTokenExpired(token);
        } catch (Exception ex) {
            logger.warn("Auth token rejected: {}", ex.toString());
            return false;
        }
    }

    private boolean isTokenExpired(String token) {
        return extractExpiration(token).before(new Date());
    }

    private Date extractExpiration(String token) {
        return extractClaim(token, Claims::getExpiration);
    }

    private <T> T extractClaim(String token, Function<Claims, T> resolver) {
        Claims claims = Jwts.parser()
                .verifyWith(key)
                .build()
                .parseSignedClaims(token)
                .getPayload();
        return resolver.apply(claims);
    }
}
