package com.naturaai.security;

import com.naturaai.model.Role;
import com.naturaai.model.User;
import com.naturaai.repository.UserRepository;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.oauth2.client.authentication.OAuth2AuthenticationToken;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.security.web.authentication.SimpleUrlAuthenticationSuccessHandler;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.UUID;

@Component
public class OAuth2SuccessHandler extends SimpleUrlAuthenticationSuccessHandler {

    private final UserRepository userRepository;
    private final JwtService jwtService;
    private final PasswordEncoder passwordEncoder;
    private final String frontendUrl;

    public OAuth2SuccessHandler(
            UserRepository userRepository,
            JwtService jwtService,
            PasswordEncoder passwordEncoder,
            @Value("${naturaai.frontend-url:http://localhost:3000}") String frontendUrl) {
        this.userRepository = userRepository;
        this.jwtService = jwtService;
        this.passwordEncoder = passwordEncoder;
        this.frontendUrl = frontendUrl;
    }

    @Override
    public void onAuthenticationSuccess(
            HttpServletRequest request,
            HttpServletResponse response,
            Authentication authentication) throws IOException, ServletException {

        OAuth2AuthenticationToken oauthToken = (OAuth2AuthenticationToken) authentication;
        OAuth2User oauthUser = oauthToken.getPrincipal();

        String rawEmail = oauthUser.getAttribute("email");
        if (rawEmail == null || rawEmail.isBlank()) {
            response.sendRedirect(frontendUrl + "/login");
            return;
        }
        String email = rawEmail.toLowerCase();

        User user = userRepository.findByEmail(email).orElseGet(() -> {
            String name = oauthUser.getAttribute("name");
            String subject = oauthUser.getAttribute("sub");
            User created = User.builder()
                    .email(email)
                    .password(passwordEncoder.encode(UUID.randomUUID().toString()))
                    .fullName(name != null && !name.isBlank() ? name : email)
                    .role(Role.USER)
                    .emailVerified(true)
                    .provider("google")
                    .providerId(subject)
                    .build();
            return userRepository.save(created);
        });

        UserPrincipal principal = new UserPrincipal(user);
        String token = jwtService.generateToken(principal);
        response.sendRedirect(frontendUrl + "/login?token=" + token);
    }
}
