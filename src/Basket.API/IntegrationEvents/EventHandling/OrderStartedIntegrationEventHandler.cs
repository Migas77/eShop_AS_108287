using eShop.Basket.API.Repositories;
using eShop.Basket.API.IntegrationEvents.EventHandling.Events;
using System.Diagnostics;
namespace eShop.Basket.API.IntegrationEvents.EventHandling;

public class OrderStartedIntegrationEventHandler(
    IBasketRepository repository,
    ILogger<OrderStartedIntegrationEventHandler> logger) : IIntegrationEventHandler<OrderStartedIntegrationEvent>
{
    private static readonly ActivitySource _activitySource = new("eShop.Basket.API.IntegrationEvents.EventHandling.OrderStartedIntegrationEventHandler");

    public async Task Handle(OrderStartedIntegrationEvent @event)
    {
        using var activity = _activitySource.StartActivity("OrderStartedIntegrationEvent handler");
        activity?.SetTag("event.id", @event.Id);
        activity?.SetTag("event.userId", @event.UserId);

        logger.LogInformation("Handling integration event: {IntegrationEventId} - ({@IntegrationEvent})", @event.Id, @event);

        var result = await repository.DeleteBasketAsync(@event.UserId);
        activity?.SetTag("event.basket.deleted", result);
        // TODO: MINE Sometimes this fails for some reason.

        if (result)
        {
            logger.LogInformation("Basket deleted for user {UserId}", @event.UserId);
        } else {
            activity?.SetStatus(ActivityStatusCode.Error, "Basket deletion failed");
            logger.LogError("Basket deletion failed for user {UserId}", @event.UserId);
        }
    }

        
}
