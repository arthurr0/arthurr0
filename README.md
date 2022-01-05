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
        logger.info("I also lead a team of several programmers with whom I work on projects");

        /*
        Projects
         */
        logger.info("minehost.pl - Hosting service for VPS and Minecraft servers.");
        logger.info("mineCodes.pl - Programmers ogrganization.");

        /*
        Development projects
         */
        logger.info("mineLogin");
        logger.severe("About: Addon for login users on Bungee, Velocity and Spigot minecraft servers.");
        logger.warning("Technology: Java, JSON, SQL, Maven, Git, Cache, bCrypt, Hashing algorithms, Messaging system.");

        logger.info("minePlots");
        logger.severe("About: Addon for create cuboids on Spigot minecraft servers.");
        logger.warning("Technology: Java, JSON, SQL, Maven, Git, mongoDB.");
    }

```
<img align="left" width="400px" src="https://github-readme-stats.vercel.app/api/wakatime?username=arturekdev&show_icons=true" />
<img align="left" width="400px" src="https://github-readme-stats.vercel.app/api?username=arturekdev&count_private=true&show_icons=true" />
