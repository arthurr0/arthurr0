```java
    public static void main(String[] args) {
        User user = new User("Arthur");
        Logger logger = Logger.getLogger("java.love");

        /*
        About me
         */
        logger.info(String.format("Hi, I'm %s!", user.getName()));
        logger.info("I am 20 years old, interested in programming since 3.5 years.");
        logger.warning("Currently doing projects based on Bukkit, Bungee and Velocity api's.");
        logger.severe("I am also staring to work in a web environment.");
        logger.info("I also lead a team of several programmers with whom I work on projects.");

        /*
        Projects
         */
        logger.info("minehost.pl - Hosting service for VPS and Minecraft servers.");
        logger.info("mineCodes.pl - Programmers ogrganization.");
        logger.info("mineLogin - Addon for login users on Bungee, Velocity and Spigot minecraft servers.");
        logger.info("minePlots - Addon for create cuboids on Spigot minecraft servers.");
    }
```
