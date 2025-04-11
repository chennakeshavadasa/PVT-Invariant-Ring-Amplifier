# PVT-Invariant-Ring-Amplifier
Design of Process Invariant Biasing of Ring Amplifiers Using Deadzone Regulation Circuit

# Acknowledgement 
This Project was done under the guidance of Praveen Kumar Venkatachala.

# Specification
- Bandwidth: 20MHz(Tsettle<250nsec)

# Schematics
- Single Ended Ring Amplifier
![WhatsApp Image 2025-04-09 at 17 53 18_316a4efe](https://github.com/user-attachments/assets/84b98bef-1db1-4f0b-96a1-14612791bf6d)

- Ring Ampllifier Stage 1
![WhatsApp Image 2025-04-11 at 18 02 13_e2c785c3](https://github.com/user-attachments/assets/e378c143-f2e7-44ac-bc56-3d9abdccdb36)

- Ring Amplifier Stage 1 Common Mode
![WhatsApp Image 2025-04-11 at 18 02 12_88d66362](https://github.com/user-attachments/assets/17124f87-9e75-4f78-9699-5873ea0e60f8)

- Ring Amplifier Stage 2
![WhatsApp Image 2025-04-11 at 18 02 13_87e2aa85](https://github.com/user-attachments/assets/e9da228a-866c-4ded-aff1-390cc53c6cd0)

- Ring Amplifier Stage 2 Replica bias
![WhatsApp Image 2025-04-11 at 18 02 13_0e1230e5](https://github.com/user-attachments/assets/52edf9c3-88fd-4922-a526-0867b114fe70)

# AC Analysis
- Note: This is in no way a representation of the stability of a Ring Amplifier. A Ring Amplifier can still exhibit ringing even with a good phase margin. The best way to verify the stability and proper operation of a Ring Amplifier is through a transient step response, since AC or STB analysis involves linearizing the system around a single operating point. In contrast, a Ring Amplifier is a dynamic system with three distinct settling phases—RC settling, large-signal settling, and small-signal settling—and involves both linear and non-linear settling behavior during its operation.

![Screenshot 2025-04-11 180900](https://github.com/user-attachments/assets/a7d6d667-cf87-42bb-aade-9051b9ec2558)

![Screenshot 2025-04-11 180823](https://github.com/user-attachments/assets/dc5dd779-621d-4228-af5d-839a0d8aea46)
 
![Screenshot 2025-04-11 180835](https://github.com/user-attachments/assets/7bff8704-ffa7-4256-8acc-5c6ac2d46012)
