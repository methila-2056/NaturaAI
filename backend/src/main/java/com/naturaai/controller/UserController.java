package com.naturaai.controller;

import com.naturaai.dto.UpdateProfileRequest;
import com.naturaai.dto.UserDto;
import com.naturaai.model.User;
import com.naturaai.model.UserProfile;
import com.naturaai.repository.UserRepository;
import com.naturaai.security.UserPrincipal;
import com.naturaai.service.AuthService;
import jakarta.validation.Valid;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.transaction.annotation.Transactional;

@RestController
@RequestMapping("/api/v1/users")
public class UserController {

    private final AuthService authService;
    private final UserRepository userRepository;

    public UserController(AuthService authService, UserRepository userRepository) {
        this.authService = authService;
        this.userRepository = userRepository;
    }

    @GetMapping("/me")
    public UserDto me(@AuthenticationPrincipal UserPrincipal principal) {
        return authService.currentUser(principal.getUsername());
    }

    @PutMapping("/me")
    @Transactional
    public UserDto update(@AuthenticationPrincipal UserPrincipal principal,
                          @Valid @RequestBody UpdateProfileRequest request) {
        User user = userRepository.findByEmail(principal.getUsername())
                .orElseThrow(() -> new IllegalArgumentException("User not found"));

        UserProfile profile = user.getProfile();
        if (profile == null) {
            profile = UserProfile.builder().user(user).build();
            user.setProfile(profile);
        }
        profile.setGender(request.gender());
        profile.setAge(request.age());
        profile.setHeight(request.height());
        profile.setWeight(request.weight());
        profile.setCountry(request.country());
        profile.setLifestyle(request.lifestyle());
        profile.setDietaryPreferences(request.dietaryPreferences());
        if (request.diseases() != null) profile.setDiseases(request.diseases());
        if (request.allergies() != null) profile.setAllergies(request.allergies());
        if (request.medications() != null) profile.setMedications(request.medications());
        userRepository.save(user);
        return UserDto.from(user);
    }
}
